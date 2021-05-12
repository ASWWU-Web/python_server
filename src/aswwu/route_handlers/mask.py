import datetime
import json
import logging
import glob
import re
import os
import io
import base64
from PIL import Image

import bleach
import tornado.web
from sqlalchemy import or_

from src.aswwu.base_handlers import BaseHandler
import src.aswwu.models.mask as mask_model
import src.aswwu.archive_models as archive_model
import src.aswwu.alchemy_new.mask as mask
import src.aswwu.alchemy_new.archive as archive
from settings import environment

logger = logging.getLogger(environment["log_name"])
PROFILE_PHOTOS_LOCATION = environment["profile_photos_location"]
PENDING_PROFILE_PHOTOS_LOCATION = environment["pending_profile_photos_location"]
CURRENT_YEAR = environment["current_year"]

# this is the root of all searches
class SearchHandler(BaseHandler):
    # accepts a year and a query as parameters
    def get(self, query_year, query):
        # if searching in the current year, access the Profile model
        server_year = self.application.options.current_year
        if query_year == server_year:
            model = mask_model.Profile
            # results = alchemy.people_db.query(model)

            # profiles = alchemy.search_all_profiles()
            # results = {r[0] for r in profiles}
        # otherwise we're going old school with the Archives
        else:
            model = archive_model.get_archive_model(query_year)
            results = archive.archive_db.query(model)
            # break up the query <-- expected to be a standard URIEncodedComponent
            fields = [q.split("=") for q in query.split(";")]
            for f in fields:
                if len(f) == 1:
                    # throw %'s around everything to make the search relative
                    # e.g. searching for "b" will return anything that has b *somewhere* in it
                    v = '%' + f[0].replace(' ', '%').replace('.', '%') + '%'
                    results = results.filter(or_(model.username.ilike(v), model.full_name.ilike(v)))
                else:
                    # we want these queries to matche exactly
                    # e.g. "%male%" would also return "female"
                    if f[0] in ['gender']:
                        results = results.filter(getattr(model, f[0]).ilike(f[1]))
                    else:
                        attribute_arr = f[1].encode('ascii', 'ignore').split(",")
                        if len(attribute_arr) > 1:
                            results = results.filter(
                                or_(getattr(model, f[0]).ilike("%" + v + "%") for v in attribute_arr))
                        else:
                            results = results.filter(getattr(model, f[0]).ilike('%' + f[1] + '%'))
            self.write({'results': [r.base_info() for r in results]})
            return

        try:
            search_criteria = {}
            # Put query into JSON form
            temp_query = query.rstrip(";")
            for q in temp_query.split(";"):
                search_criteria[q.split("=")[0]] = q.split("=")[1]
            results = mask.search_profiles(search_criteria)
        except:
            search_criteria = query
            # If there's no search parameters
            if len(search_criteria) == 0:
                results = mask.search_all_profiles()
            # If only a username is being passed into the search parameters
            elif len(search_criteria) > 0:
                search_criteria = {"username": search_criteria.replace(' ', '%').replace('.', '%')}
                results = mask.search_profiles(search_criteria)
        keys = ['username', 'full_name', 'photo', 'email', 'views']
        self.write({'results': [r[0].to_json(views=r[1], limitList=keys) for r in results]})


# get 10 (username, full_name) pairs based on query of fullname
class SearchNamesFast(BaseHandler):
    def get(self):
        search_criteria = {}
        for key, value in self.request.arguments.items():
            search_criteria[key] = value[0]
        names = mask.search_profile_names(search_criteria.get('full_name', ''), limit=int(search_criteria.get('limit', 5)))
        self.write({'results': [{'username': pair[0], 'full_name': pair[1]} for pair in names]})


# get all of the profiles in our database
class SearchAllHandler(BaseHandler):
    def get(self):
        # cache client side for 24 hours, server side caching in nginx
        self.add_header('Cache-control', 'max-age=86400')
        self.add_header('Cache-control', 'public')
        profiles = mask.search_all_profiles()
        keys = ['username', 'full_name', 'photo', 'email']
        self.write({'results': [r.to_json(limitList=keys) for r in profiles]})

# get user's profile information
class ProfileHandler(BaseHandler):
    def get(self, year, username):
        # check if we're looking at the current year or going old school
        if year == tornado.options.options.current_year:
            profile = mask.people_db.query(mask_model.Profile).filter_by(username=str(username)).all()
        else:
            profile = archive.archive_db.query(archive_model.get_archive_model(year)).filter_by(username=str(username)).all()
        # some quick error checking
        if len(profile) == 0:
            self.write({'error': 'no profile found'})
        elif len(profile) > 1:
            self.write({'error': 'too many profiles found'})
        else:
            profile = profile[0]
            user = self.get_current_user()
            # if the user is logged in and isn't vainly looking at themselves
            # then we assume the searched for user is popular and give them a +1
            referer = self.request.headers.get('Referer')
            if referer is not None and "mask" in referer:
                update_views(user, profile, year)
            if not user:
                if profile.privacy == 1:
                    self.write(profile.impers_info())
                else:
                    self.write(profile.base_info())
            else:
                if user.username == profile.username:
                    self.write(profile.to_json())
                else:
                    self.write(profile.view_other())


def update_views(user, profile, year):
    if user and str(user.wwuid) != str(profile.wwuid) and year == tornado.options.options.current_year:
        views = mask.people_db.query(mask_model.ProfileView)\
            .filter_by(viewer=user.username, viewed=profile.username).all()
        if len(views) == 0:
            view = mask_model.ProfileView()
            view.viewer = user.username
            view.viewed = profile.username
            view.last_viewed = datetime.datetime.now()
            view.num_views = 1
            mask.add_or_update(view)
        else:
            for view in views:
                if (datetime.datetime.now() - view.last_viewed).total_seconds() > 7200:
                    view.num_views += 1
                    view.last_viewed = datetime.datetime.now()
                    mask.add_or_update(view)


# this updates profile information - not much to it
class ProfileUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, username):
        user = self.current_user
        if user.username == username or 'administrator' in user.roles:
            if user.username != username:
                f = open('adminLog', 'w')
                f.write(user.username + " is updating the profile of " + username + "\n")
                f.close()
            profile = mask.people_db.query(mask_model.Profile).filter_by(username=str(username)).one()
            profile.full_name = bleach.clean(self.get_argument('full_name'))
            profile.photo = bleach.clean(self.get_argument('photo', ''))
            profile.gender = bleach.clean(self.get_argument('gender', ''))
            profile.birthday = bleach.clean(self.get_argument('birthday', ''))
            profile.email = bleach.clean(self.get_argument('email', ''))
            profile.phone = bleach.clean(self.get_argument('phone', ''))
            profile.majors = bleach.clean(self.get_argument('majors', ''))
            profile.minors = bleach.clean(self.get_argument('minors', ''))
            profile.graduate = bleach.clean(self.get_argument('graduate', ''))
            profile.preprofessional = bleach.clean(self.get_argument('preprofessional', ''))
            profile.class_standing = bleach.clean(self.get_argument('class_standing', ''))
            profile.high_school = bleach.clean(self.get_argument('high_school', ''))
            profile.class_of = bleach.clean(self.get_argument('class_of', ''))
            profile.relationship_status = bleach.clean(self.get_argument('relationship_status', ''))
            profile.attached_to = bleach.clean(self.get_argument('attached_to', ''))
            profile.quote = bleach.clean(self.get_argument('quote', ''))
            profile.quote_author = bleach.clean(self.get_argument('quote_author', ''))
            profile.hobbies = bleach.clean(self.get_argument('hobbies', ''))
            profile.career_goals = bleach.clean(self.get_argument('career_goals', ''))
            profile.favorite_books = bleach.clean(self.get_argument('favorite_books', ''))
            profile.favorite_food = bleach.clean(self.get_argument('favorite_food', ''))
            profile.favorite_movies = bleach.clean(self.get_argument('favorite_movies', ''))
            profile.favorite_music = bleach.clean(self.get_argument('favorite_music', ''))
            profile.pet_peeves = bleach.clean(self.get_argument('pet_peeves', ''))
            profile.personality = bleach.clean(self.get_argument('personality', ''))
            profile.privacy = bleach.clean(self.get_argument('privacy', ''))
            profile.website = bleach.clean(self.get_argument('website', ''))
            if user.status != "Student":
                profile.department = bleach.clean(self.get_argument('department', ''))
                profile.office = bleach.clean(self.get_argument('office', ''))
                profile.office_hours = bleach.clean(self.get_argument('office_hours', ''))

            mask.add_or_update(profile)
            self.write(json.dumps('success'))
        else:
            self.write({'error': 'invalid permissions'})

class UploadProfilePhotoHandler(BaseHandler):
    def post(self):
        try:
            image_base64 = self.get_argument("image")
            image_name = self.get_argument("name")
            image = Image.open(io.BytesIO(base64.b64decode(image_base64))) # https://stackoverflow.com/questions/26070547/decoding-base64-from-post-to-use-in-pil
            image_path = PENDING_PROFILE_PHOTOS_LOCATION + "/" + image_name
            image.save(image_path)
            self.write({'link': image_path})
        except Exception as e:
            logger.info(e)
            raise Exception(e)
    get = post # https://stackoverflow.com/questions/19006783/tornado-post-405-method-not-allowed

class DirectUploadProfilePhotoHandler(BaseHandler):
    '''
        Upload a profile photo directly to the server
    '''
    def post(self):
        try:
            user = self.current_user
            if 'mask-admin' in user.roles:
                image_base64 = self.get_argument("image")
                image_name = self.get_argument("name")
                image = Image.open(io.BytesIO(base64.b64decode(image_base64))) # https://stackoverflow.com/questions/26070547/decoding-base64-from-post-to-use-in-pil
                image_path = PROFILE_PHOTOS_LOCATION + "/" + image_name
                image.save(image_path)
                self.write({'link': image_path})
            else:
                raise Exception("You do not have permission to upload files")
        except Exception as e:
            logger.info(e)
            raise Exception(e)
    get = post # https://stackoverflow.com/questions/19006783/tornado-post-405-method-not-allowed

class VerifyMaskUploadPermissions(BaseHandler):
    '''
        Verify  Permissions to upload to mask.
    '''
    def post(self):
        try:
            if self.current_user:
                user = self.current_user
                if 'mask-admin' in user.roles:
                    self.write({'permission': True})
                else:
                    self.write({'permission': False})
            else:
                raise Exception("You must be logged in!")
        except Exception as e:
            logger.info(e)
            raise Exception(e)
    get = post # https://stackoverflow.com/questions/19006783/tornado-post-405-method-not-allowed

class ListProfilePhotoHandler(BaseHandler):
    '''
    Return the authenticated user's profile pictures, example: {"photos": ["profiles/1718/12345_1234567.jpg"]}
    '''
    @tornado.web.authenticated
    def get(self):
        try:
            wwuid = str(self.current_user.wwuid)
            glob_pattern = PROFILE_PHOTOS_LOCATION + '/*/*-' + wwuid + '.*' # SEARCHING WITH DASH
            photo_list = glob.glob(glob_pattern)
            photo_list = ['profiles' + photo.replace(PROFILE_PHOTOS_LOCATION, '') for photo in photo_list]
            self.write({'photos': photo_list})
        except Exception as e:
            logger.info(e)
            raise Exception(e)

class ListPendingProfilePhotoHandler(BaseHandler):
    '''
    Return the authenticated user's pending profile pictures, example: {"photos": ["pending_profiles/12345_1234567.jpg"]}
    '''
    @tornado.web.authenticated
    def get(self):
        try:
            wwuid = str(self.current_user.wwuid)
            glob_pattern = PENDING_PROFILE_PHOTOS_LOCATION + '/*.*'
            photo_list = glob.glob(glob_pattern)
            photo_list = ['pending_profiles' + photo.replace(PENDING_PROFILE_PHOTOS_LOCATION, '') for photo in photo_list]
            self.write({'photos': photo_list})
        except Exception as e:
            logger.info(e)
            raise Exception(e)

from datetime import datetime, UTC
import json
import logging
import glob
import io
import base64
import os
from PIL import Image, ImageOps

import bleach
import tornado.web
from sqlalchemy import or_, select

from src.aswwu.base_handlers import BaseHandler
import src.aswwu.models.mask as mask_model
import src.aswwu.archive_models as archive_model
import src.aswwu.alchemy_engines.mask as mask
import src.aswwu.alchemy_engines.archive as archive
from settings import config, buildMediaPath

logger = logging.getLogger(config.logging.get('log_name'))
PROFILE_PHOTOS_LOCATION = buildMediaPath("profiles")
PENDING_PROFILE_PHOTOS_LOCATION = buildMediaPath("pending_profile_photos")
DISMAYED_PROFILE_PHOTOS_LOCATION = buildMediaPath("dismayed_profile_photos")
CURRENT_YEAR = config.mask.get('current_year')
MEDIA_LOCATION = buildMediaPath("")

# this is the root of all searches
class SearchHandler(BaseHandler):
    # accepts a year and a query as parameters
    def get(self, query_year: str, query: str):
        # if searching in the current year, access the Profile model
        server_year = self.application.options.current_year
        # If the query year is not the current year, we're going old school with the Archives
        if query_year != server_year:
            model = archive_model.get_archive_model(query_year)
            results = archive.archive_db.query(model)
            # break up the query <-- expected to be a standard URIEncodedComponent
            fields = [q.split("=") for q in query.split(";")]
            for f in fields:
                match len(f):
                    case 0:
                        break
                    case 1:
                        # throw %'s around everything to make the search relative
                        # e.g. searching for "b" will return anything that has b *somewhere* in it
                        v = '%' + f[0].replace(' ', '%').replace('.', '%') + '%'
                        results = results.filter(or_(model.username.ilike(v), model.full_name.ilike(v)))
                    case _:
                        # we want these queries to matche exactly
                        # e.g. "%male%" would also return "female"
                        if f[0] in ['gender']:
                            results = results.filter(getattr(model, f[0]).ilike(f[1]))
                        else:
                            attribute_arr = f[1].split(",")
                            if len(attribute_arr) > 1:
                                results = results.filter(
                                    or_(getattr(model, f[0]).ilike("%" + v + "%") for v in attribute_arr))
                            else:
                                results = results.filter(getattr(model, f[0]).ilike('%' + f[1] + '%'))
                match len(f):
                    case 0:
                        break
                    case 1:
                        # throw %'s around everything to make the search relative
                        # e.g. searching for "b" will return anything that has b *somewhere* in it
                        v = '%' + f[0].replace(' ', '%').replace('.', '%') + '%'
                        results = results.filter(or_(model.username.ilike(v), model.full_name.ilike(v)))
                    case _:
                        # we want these queries to matche exactly
                        # e.g. "%male%" would also return "female"
                        if f[0] in ['gender']:
                            results = results.filter(getattr(model, f[0]).ilike(f[1]))
                        else:
                            attribute_arr = f[1].split(",")
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
        # NOTE: Is this really the best way to do this?
        self.write({'results': [{'username': r[0], 'full_name': r[1], 'photo': r[2], 'email': r[3]} for r in results]})


# get 5 (username, full_name) pairs based on query of fullname
class SearchNamesFast(BaseHandler):
    def get(self):
        search_criteria = {}
        for key, value in self.request.arguments.items():
            # convert to str
            search_criteria[key] = value[0].decode('utf-8')
        

        names = mask.search_profile_names(search_criteria.get('full_name', ''), limit=int(search_criteria.get('limit', 5)))
        # if no names are found, return an empty list
        if names == None:
            self.write({'results': []})
            return
        self.write({'results': [{'username': pair[0], 'full_name': pair[1]} for pair in names]})


# get all of the profiles in our database
class SearchAllHandler(BaseHandler):
    def get(self):
        profiles = mask.search_all_profiles()
        if profiles == None:
            self.write({'error': 'no profiles found'})
            return

        self.write({'results': [{'username': r[0], 'full_name': r[1], 'photo': r[2], 'email': r[3]} for r in profiles]})

# get user's profile information
class ProfileHandler(BaseHandler):
    def get(self, year, username):
        # check if we're looking at the current year or going old school
        if year == tornado.options.options.current_year:
            stmt = select(mask_model.Profile).filter_by(username=str(username))
            profile = mask.people_db.execute(stmt).all()
        else:
            stmt = select(archive_model.get_archive_model(year)).filter_by(username=str(username))
            profile = archive.archive_db.execute(stmt).all()
        # some quick error checking
        if len(profile) == 0 or len(profile[0]) == 0:
            self.write({'error': 'no profile found'})
        elif len(profile) > 1 or len(profile[0]) > 1:
            self.write({'error': 'too many profiles found'})
        else:
            profile = profile[0][0]
            user = self.get_current_user()
            if not user:
                # this accounts for the archived profiles using the inverse of the privacy setting
                # Riley: I changed this because of how the UI renders the privacy setting.
                # additionally I believe it makes more sense for the profile to be private if the value is true
                if profile.privacy == 0 and year == CURRENT_YEAR:
                    self.write(profile.impers_info())
                elif profile.privacy == 1 and year != CURRENT_YEAR:
                    self.write(profile.impers_info())
                else:
                    self.write(profile.base_info())
            else:
                if user.username == profile.username:
                    self.write(profile.to_json())
                else:
                    self.write(profile.view_other())


# this updates profile information - not much to it
class ProfileUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, username):
        user = self.get_current_user()
        data = json.loads(self.request.body)
        if user.username == username or 'administrator' in user.roles:
            if user.username != username:
                f = open('adminLog', 'w')
                f.write(user.username + " is updating the profile of " + username + "\n")
                f.close()
            profile = mask.query_by_wwuid(mask_model.Profile, user.wwuid)[0]
            # todo: we should probably do some validation here. look into pydantic
            # TODO: bleach is deprecated, we should probably move to NH3 or something
            profile.full_name = bleach.clean(data.get('full_name'))
            profile.photo = bleach.clean(data.get('photo', ''))
            profile.gender = bleach.clean(data.get('gender', ''))
            profile.birthday = self.format_date(bleach.clean(data.get('birthday', '')))
            profile.email = bleach.clean(data.get('email', ''))
            profile.phone = bleach.clean(data.get('phone', ''))
            profile.majors = bleach.clean(data.get('majors', ''))
            profile.minors = bleach.clean(data.get('minors', ''))
            profile.graduate = bleach.clean(data.get('graduate', ''))
            profile.preprofessional = bleach.clean(data.get('preprofessional', ''))
            profile.class_standing = bleach.clean(data.get('class_standing', ''))
            profile.high_school = bleach.clean(data.get('high_school', ''))
            profile.class_of = bleach.clean(data.get('class_of', ''))
            profile.relationship_status = bleach.clean(data.get('relationship_status', ''))
            profile.attached_to = bleach.clean(data.get('attached_to', ''))
            profile.quote = bleach.clean(data.get('quote', ''))
            profile.quote_author = bleach.clean(data.get('quote_author', ''))
            profile.hobbies = bleach.clean(data.get('hobbies', ''))
            profile.career_goals = bleach.clean(data.get('career_goals', ''))
            profile.favorite_books = bleach.clean(data.get('favorite_books', ''))
            profile.favorite_food = bleach.clean(data.get('favorite_food', ''))
            profile.favorite_movies = bleach.clean(data.get('favorite_movies', ''))
            profile.favorite_music = bleach.clean(data.get('favorite_music', ''))
            profile.pet_peeves = bleach.clean(data.get('pet_peeves', ''))
            profile.personality = bleach.clean(data.get('personality', ''))
            profile.privacy = bleach.clean(data.get('privacy', ''))
            profile.website = bleach.clean(data.get('website', ''))
            if user.status != "Student":
                profile.department = bleach.clean(data.get('department', ''))
                profile.office = bleach.clean(data.get('office', ''))
                profile.office_hours = bleach.clean(data.get('office_hours', ''))

            mask.add_or_update(profile)
            self.write(json.dumps('success'))
        else:
            self.write({'error': 'invalid permissions'})

    # format the date for the frontend. we don't store years.
    # this may change in the future
    def format_date(self, input):
        try:
            date = datetime.strptime(input, '%Y-%m-%d')
            date.year = datetime.now().year
            return date.strftime('%m-%d-%Y')
        except:
            return input

# upload profile photos
class UploadProfilePhotoHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body)
        if not data.get('image'):
            self.set_status(status_code=400)
            self.write({'error': 'incorrect format'})
            self.flush()
            return
        try:
            image_base64 = data.get('image')
            self.process_image(image_base64)
            self.write({'success': True})
        except Exception as error:
            logger.info(error)
            raise Exception(error)
    get = post   # https://stackoverflow.com/questions/19006783/tornado-post-405-method-not-allowed

    def process_image(self, image):
        # make a pillow object from the base64 string
        image = Image.open(io.BytesIO(base64.b64decode(image)))
        # create the name and path
        image_name = f'{self.current_user.wwuid}_{int(datetime.now(UTC).timestamp() * 1000)}'
        image_path = f'{PENDING_PROFILE_PHOTOS_LOCATION}/{image_name}.jpg'
        # transpose the image
        image = ImageOps.exif_transpose(image)

        # convert to RGB/JPEG
        rgb_image = image.convert('RGB')
        # Save the image, reducing the quality to 75% and optimizing
        # This is so we have a smaller image size in general.
        # We can do some further optimizations by implementing an image proxy. But that is for later.
        rgb_image.save(image_path, quality=75, optimize=True)

        # close the images
        image.close()
        rgb_image.close()

# list profile photos
class ListProfilePhotoHandler(BaseHandler):
    '''
    Return the authenticated user's profile pictures, example: {"photos": ["profiles/1718/12345_1234567.jpg"]}
    '''
    @tornado.web.authenticated
    def get(self):
        try:
            wwuid = str(self.current_user.wwuid)
            glob_pattern = PROFILE_PHOTOS_LOCATION + '/*/' + wwuid + '_*.*' # SEARCHING WITH DASH
            photo_list = glob.glob(glob_pattern)
            photo_list = ['profiles' + photo.replace(PROFILE_PHOTOS_LOCATION, '') for photo in photo_list]
            self.write({'photos': photo_list})
        except Exception as e:
            logger.info(e)
            raise Exception(e)

# -- moderation --

# list pending profile photos
class ListPendingProfilePhotoHandler(BaseHandler):
    '''
    Return the authenticated user's pending profile pictures, example: {"photos": ["pending_profiles/12345_1234567.jpg"]}
    '''
    @tornado.web.authenticated
    def get(self):
        try:
            glob_pattern = PENDING_PROFILE_PHOTOS_LOCATION + '/*.*'
            photo_list = glob.glob(glob_pattern)
            photo_list = ['pending_profile_photos' + photo.replace(PENDING_PROFILE_PHOTOS_LOCATION, '') for photo in photo_list]
            print(photo_list)
            self.write({'photos': photo_list})
        except Exception as e:
            logger.info(e)
            raise Exception(e)

# approve profile photos
class ApproveImageHandler(BaseHandler):
    def get(self, filename):
        pending_image_name = MEDIA_LOCATION + "/" + filename
        glob_results = glob.glob(pending_image_name)
        if not glob_results:
            self.write({'error': 'could not find: ' + filename})
            return
        destination_directory = PROFILE_PHOTOS_LOCATION + "/" + CURRENT_YEAR
        if not os.path.exists(destination_directory):
            os.mkdir(destination_directory)
        image_id = filename.split("/")[1]
        destination_path = destination_directory + "/" + image_id
        os.rename(pending_image_name, destination_path)
        glob_pattern = PENDING_PROFILE_PHOTOS_LOCATION + '/*.*' # SEARCHING WITH DASH
        photo_list = glob.glob(glob_pattern)
        photo_list = ['pending_profile_photos' + photo.replace(PENDING_PROFILE_PHOTOS_LOCATION, '') for photo in photo_list]
        self.write({'photos': photo_list})

# dismay profile photos
class DismayImageHandler(BaseHandler):
    def get(self, filename):
        pending_image_name = MEDIA_LOCATION + "/" + filename
        glob_results = glob.glob(pending_image_name)
        if not glob_results:
            self.write({'error': 'could not find: ' + filename})
            return
        destination_directory = DISMAYED_PROFILE_PHOTOS_LOCATION + "/" + CURRENT_YEAR
        if not os.path.exists(destination_directory):
            os.mkdir(destination_directory)
        image_id = filename.split("/")[1]
        destination_path = destination_directory + "/" + image_id
        os.rename(pending_image_name, destination_path)
        glob_pattern = PENDING_PROFILE_PHOTOS_LOCATION + '/*.*' # SEARCHING WITH DASH
        photo_list = glob.glob(glob_pattern)
        photo_list = ['pending_profile_photos' + photo.replace(PENDING_PROFILE_PHOTOS_LOCATION, '') for photo in photo_list]
        self.write({'photos': photo_list})
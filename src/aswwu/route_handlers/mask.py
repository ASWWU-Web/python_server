import datetime
import json
import logging

import bleach
import tornado.web
from sqlalchemy import or_

from src.aswwu.base_handlers import BaseHandler
import src.aswwu.models.mask as mask_model
import src.aswwu.archive_models as archives
import src.aswwu.alchemy as alchemy

logger = logging.getLogger("aswwu")


# administrative role handler
class AdministratorRoleHandler(BaseHandler):
    # decorator to force them to be logged in to access this information
    # also only accepts post requests right now
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        # check if they have valid permissions
        if 'administrator' not in user.roles:
            self.write({'error': 'insufficient permissions'})
        else:
            cmd = self.get_argument('cmd', None)
            # grant permissions to other users
            # sharing is caring
            if cmd == 'set_role':
                username = self.get_argument('username', '').replace(' ', '.').lower()
                fuser = alchemy.people_db.query(mask_model.User).filter_by(username=username).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    if fuser.roles is None:
                        fuser.roles = ''
                    # roles are a comma separated list
                    # so we have to do some funkiness to append and then rejoin that list in the database
                    roles = fuser.roles.split(', ')
                    roles.append(self.get_argument('newRole', None))
                    roles = set(roles)
                    fuser.roles = ', '.join(roles)
                    alchemy.add_or_update(fuser)
                    self.write({'response': 'success'})


# this is the root of all searches
class SearchHandler(BaseHandler):
    # accepts a year and a query as parameters
    def get(self, year, query):
        # if searching in the current year, access the Profile model
        if year == self.application.options.current_year:
            model = mask_model.Profile
            results = alchemy.people_db.query(model)
        # otherwise we're going old school with the Archives
        else:
            model = archives.get_archive_model(year)
            results = alchemy.archive_db.query(model)

        # break up the query <-- expected to be a standard URIEncodedComponent
        fields = [q.split("=") for q in query.split(";")]
        for f in fields:
            if len(f) == 1:
                # throw %'s around everything to make the search relative
                # e.g. searching for "b" will return anything that has b *somewhere* in it
                v = '%'+f[0].replace(' ', '%').replace('.', '%')+'%'
                results = results.filter(or_(model.username.ilike(v), model.full_name.ilike(v)))
            else:
                # we want these queries to matche exactly
                # e.g. "%male%" would also return "female"
                if f[0] in ['gender']:
                    results = results.filter(getattr(model, f[0]).ilike(f[1]))
                else:
                    attribute_arr = f[1].encode('ascii', 'ignore').split(",")
                    if len(attribute_arr) > 1:
                        results = results.filter(or_(getattr(model, f[0]).ilike("%" + v + "%") for v in attribute_arr))
                    else:
                        results = results.filter(getattr(model, f[0]).ilike('%'+f[1]+'%'))
        self.write({'results': [r.base_info() for r in results]})


# get all of the profiles in our database
class SearchAllHandler(BaseHandler):
    def get(self):
        profiles = alchemy.query_all(mask_model.Profile)
        self.write({'results': [p.base_info() for p in profiles]})


# get user's profile information
class ProfileHandler(BaseHandler):
    def get(self, year, username):
        # check if we're looking at the current year or going old school
        if year == tornado.options.options.current_year:
            profile = alchemy.people_db.query(mask_model.Profile).filter_by(username=str(username)).all()
        else:
            profile = alchemy.archive_db.query(archives.get_archive_model(year)).filter_by(username=str(username)).all()
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
            update_views(user, profile, year)
            # self.write(profile.to_json())
            if not user:
                if profile.privacy == 1:
                    self.write(profile.impers_info())
                else:
                    self.write(profile.no_info())
            else:
                if user.username == profile.username:
                    self.write(profile.to_json())
                else:
                    self.write(profile.view_other())


def update_views(user, profile, year):
    if user and str(user.wwuid) != str(profile.wwuid) and year == tornado.options.options.current_year:
        views = alchemy.people_db.query(mask_model.ProfileView)\
            .filter_by(viewer=user.username, viewed=profile.username).all()
        if len(views) == 0:
            view = mask_model.ProfileView()
            view.viewer = user.username
            view.viewed = profile.username
            view.last_viewed = datetime.datetime.now()
            view.num_views = 1
            alchemy.add_or_update(view)
        else:
            for view in views:
                if (datetime.datetime.now() - view.last_viewed).total_seconds() > 7200:
                    view.num_views += 1
                    view.last_viewed = datetime.datetime.now()
                    alchemy.add_or_update(view)


# queries the server for a user's photos
class ProfilePhotoHandler(BaseHandler):
    def get(self, year, wwuid_or_username):
        wwuid = None
        username = None
        if len(wwuid_or_username.split(".")) == 1:
            wwuid = wwuid_or_username
        else:
            username = wwuid_or_username
        # check if we're looking at current photos or not
        if year == self.application.options.current_year:
            if wwuid:
                profile = alchemy.query_by_wwuid(mask_model.Profile, wwuid)
            else:
                profile = alchemy.people_db.query(mask_model.Profile).filter_by(username=str(username)).all()
        else:
            if wwuid:
                profile = alchemy.archive_db.query(archives.get_archive_model(year)).filter_by(wwuid=str(wwuid)).all()
            else:
                profile = alchemy.archive_db.query(archives.get_archive_model(year))\
                    .filter_by(username=str(username)).all()
        if len(profile) == 0:
            self.write({'error': 'no profile found'})
        elif len(profile) > 1:
            self.write({'error': 'too many profiles found'})
        else:
            # now we've got just one profile, return the photo field attached to a known photo URI
            profile = profile[0]
            self.redirect("https://aswwu.com/media/img-sm/"+str(profile.photo))


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
            profile = alchemy.people_db.query(mask_model.Profile).filter_by(username=str(username)).one()
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

            alchemy.add_or_update(profile)
            self.write(json.dumps('success'))
        else:
            self.write({'error': 'invalid permissions'})


class MatcherHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user

        if 'matcher' in user.roles:
            profiles = alchemy.query_all(mask_model.Profile)
            self.write({'database': [p.view_other() for p in profiles]})
        else:
            self.write("{'error': 'Insufficient Permissions :('}")

import tornado.web
import logging
import requests
import json
import datetime
from sqlalchemy import or_
from alchemy.models import *
from alchemy.archive_models import *
from alchemy.setup import *

from alchemy.base_handlers import BaseHandler

logger = logging.getLogger("aswwu")


class ListProfilesHandler(BaseHandler):
    def get(self):
        profiles = query_all(Profile)
        self.write({'results': [p.base_info() for p in profiles]})


class SearchHandler(BaseHandler):
    def get(self, year, query):
        if year == self.application.options.current_year:
            model = Profile
            results = s.query(model)
        else:
            model = globals()['Archive'+str(year)]
            results = archive_s.query(model)

        fields = [q.split("=") for q in query.split(";")]
        for f in fields:
            if len(f) == 1:
                v = '%'+f[0].replace(' ','%').replace('.','%')+'%'
                results = results.filter(or_(model.username.ilike(v), model.full_name.ilike(v)))
            else:
                if f[0] in ['gender']:
                    results = results.filter(getattr(model,f[0]).ilike(f[1]))
                else:
                    results = results.filter(getattr(model,f[0]).ilike('%'+f[1]+'%'))
        self.write({'results': [r.base_info() for r in results]})


class ProfileHandler(BaseHandler):
    def get(self, year, username):
        if year == self.application.options.current_year:
            profile = s.query(Profile).filter_by(username=str(username)).all()
        else:
            profile = archive_s.query(globals()['Archive'+str(year)]).filter_by(username=str(username)).all()
        if len(profile) == 0:
            self.write({'error': 'no profile found'})
        elif len(profile) > 1:
            self.write({'error': 'too many profiles found'})
        else:
            profile = profile[0]
            user = self.current_user
            if user and user.wwuid != profile.wwuid and year == self.application.options.current_year:
                profile.views = profile.views+1
                addOrUpdate(profile)
            self.write(profile.to_json())


class UpdateProfileHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, username):
        user = self.current_user
        if user.username == username or 'administrator' in user.roles:
            profile = s.query(Profile).filter_by(username=str(username)).one()
            profile.photo = self.get_argument('photo','')
            profile.gender = self.get_argument('gender','')
            profile.birthday = self.get_argument('birthday','')
            profile.email = self.get_argument('email','')
            profile.phone = self.get_argument('phone','')
            profile.majors = self.get_argument('majors','')
            profile.minors = self.get_argument('minors','')
            profile.graduate = self.get_argument('graduate','')
            profile.preprofessional = self.get_argument('preprofessional','')
            profile.class_standing = self.get_argument('class_standing','')
            profile.high_school = self.get_argument('high_school','')
            profile.class_of = self.get_argument('class_of','')
            profile.relationship_status = self.get_argument('relationship_status','')
            profile.attached_to = self.get_argument('attached_to','')
            profile.quote = self.get_argument('quote','')
            profile.quote_author = self.get_argument('quote_author','')
            profile.hobbies = self.get_argument('hobbies','')
            profile.career_goals = self.get_argument('career_goals','')
            profile.favorite_books = self.get_argument('favorite_books','')
            profile.favorite_food = self.get_argument('favorite_food','')
            profile.favorite_movies = self.get_argument('favorite_food','')
            profile.favorite_music = self.get_argument('favorite_music','')
            profile.pet_peeves = self.get_argument('pet_peeves','')
            profile.personality = self.get_argument('personality','')
            profile.privacy = self.get_argument('privacy','')
            if user.status != "Student":
                profile.department = self.get_argument('department','')
                profile.office = self.get_argument('office','')
                profile.office_hours = self.get_argument('office_hours','')

            addOrUpdate(profile)
            self.write(json.dumps('success'))
        else:
            self.write({'error': 'invalid permissions'})

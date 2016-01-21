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

class AdministratorRoleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        if 'administrator' not in user.roles:
            self.write({'error': 'insufficient permissions'})
        else:
            cmd = self.get_argument('cmd', None)
            if cmd == 'set_role':
                username = self.get_argument('username', '').replace(' ','.').lower()
                fuser = s.query(User).filter_by(username=username).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    if fuser.roles is None:
                        fuser.roles = ''
                    roles = fuser.roles.split(',')
                    roles.append(self.get_argument('newRole', None))
                    roles = set(roles)
                    fuser.roles = (',').join(roles)
                    addOrUpdate(fuser)
                    self.write({'response': 'success'})


class CollegianRoleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        if 'collegian' not in user.roles and 'collegian_admin' not in user.roles:
            return self.write({'error': 'insufficient permissions'})

        id = self.get_argument('id',None)
        volume = self.get_argument('volume',None)
        issue = self.get_argument('issue',None)
        title = self.get_argument('title',None)
        author = self.get_argument('author',None)
        if 'collegian_admin' not in user.roles:
            author = user.full_name
        section = self.get_argument('section',None)
        content = self.get_argument('content',None)

        if not volume or not issue or not title or not author or not section or not content:
            return self.write({'error': 'you must provide a volume, issue, title, author, section, and content for an article'})

        logger.debug(id)
        if id is not None and id != '':
            collegian_article = query_by_id(CollegianArticle, id)
            if not collegian_article:
                return self.write({'error': 'no Collegian Article with that ID exists'})
        else:
            collegian_article = CollegianArticle()

        collegian_article.volume = volume
        collegian_article.issue = issue
        collegian_article.title = title
        collegian_article.author = author
        collegian_article.section = section
        collegian_article.content = content

        addOrUpdate(collegian_article)
        self.write({'response': 'success'})


class VolunteerRoleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        if 'volunteer' not in user.roles:
            self.write({'error': 'insufficient permissions'})
        else:
            cmd = self.get_argument('cmd', None)
            logger.debug(cmd)
            if cmd == 'set_role':
                username = self.get_argument('username', '').replace(' ','.').lower()
                fuser = s.query(User).filter_by(username=username).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    if fuser.roles is None:
                        fuser.roles = ''
                    roles = fuser.roles.split(',')
                    roles.append('volunteer')
                    roles = set(roles)
                    fuser.roles = (',').join(roles)
                    addOrUpdate(fuser)
                    self.write({'response': 'success'})
            elif cmd == 'search' or cmd == 'viewPrintOut':
                volunteers = s.query(Volunteer)
                if self.get_argument('campus_ministries', '') == 'on':
                    volunteers = volunteers.filter_by(campus_ministries=True)
                if self.get_argument('student_missions', '') == 'on':
                    volunteers = volunteers.filter_by(student_missions=True)
                if self.get_argument('aswwu', '') == 'on':
                    volunteers = volunteers.filter_by(aswwu=True)
                if self.get_argument('circle_church', '') == 'on':
                    volunteers = volunteers.filter_by(circle_church=True)
                if self.get_argument('university_church', '') == 'on':
                    volunteers = volunteers.filter_by(university_church=True)
                if self.get_argument('buddy_program', '') == 'on':
                    volunteers = volunteers.filter_by(buddy_program=True)
                if self.get_argument('assist', '') == 'on':
                    volunteers = volunteers.filter_by(assist=True)
                if self.get_argument('lead', '') == 'on':
                    volunteers = volunteers.filter_by(lead=True)
                if self.get_argument('audio_slash_visual', '') == 'on':
                    volunteers = volunteers.filter_by(audio_slash_visual=True)
                if self.get_argument('health_promotion', '') == 'on':
                    volunteers = volunteers.filter_by(health_promotion=True)
                if self.get_argument('construction_experience', '') == 'on':
                    volunteers = volunteers.filter_by(construction_experience=True)
                if self.get_argument('outdoor_slash_camping', '') == 'on':
                    volunteers = volunteers.filter_by(outdoor_slash_camping=True)
                if self.get_argument('concert_assistance', '') == 'on':
                    volunteers = volunteers.filter_by(concert_assistance=True)
                if self.get_argument('event_set_up', '') == 'on':
                    volunteers = volunteers.filter_by(event_set_up=True)
                if self.get_argument('children_ministries', '') == 'on':
                    volunteers = volunteers.filter_by(children_ministries=True)
                if self.get_argument('children_story', '') == 'on':
                    volunteers = volunteers.filter_by(children_story=True)
                if self.get_argument('art_poetry_slash_painting_slash_sculpting', '') == 'on':
                    volunteers = volunteers.filter_by(art_poetry_slash_painting_slash_sculpting=True)
                if self.get_argument('organizing_events', '') == 'on':
                    volunteers = volunteers.filter_by(organizing_events=True)
                if self.get_argument('organizing_worship_opportunities', '') == 'on':
                    volunteers = volunteers.filter_by(organizing_worship_opportunities=True)
                if self.get_argument('organizing_community_outreach', '') == 'on':
                    volunteers = volunteers.filter_by(organizing_community_outreach=True)
                if self.get_argument('bible_study', '') == 'on':
                    volunteers = volunteers.filter_by(bible_study=True)
                if self.get_argument('wycliffe_bible_translator_representative', '') == 'on':
                    volunteers = volunteers.filter_by(wycliffe_bible_translator_representative=True)
                if self.get_argument('food_preparation', '') == 'on':
                    volunteers = volunteers.filter_by(food_preparation=True)
                if self.get_argument('graphic_design', '') == 'on':
                    volunteers = volunteers.filter_by(graphic_design=True)
                if self.get_argument('poems_slash_spoken_word', '') == 'on':
                    volunteers = volunteers.filter_by(poems_slash_spoken_word=True)
                if self.get_argument('prayer_team_slash_prayer_house', '') == 'on':
                    volunteers = volunteers.filter_by(prayer_team_slash_prayer_house=True)
                if self.get_argument('dorm_encouragement_and_assisting_chaplains', '') == 'on':
                    volunteers = volunteers.filter_by(dorm_encouragement_and_assisting_chaplains=True)
                if self.get_argument('scripture_reading', '') == 'on':
                    volunteers = volunteers.filter_by(scripture_reading=True)
                if self.get_argument('speaking', '') == 'on':
                    volunteers = volunteers.filter_by(speaking=True)
                if self.get_argument('videography', '') == 'on':
                    volunteers = volunteers.filter_by(videography=True)
                if self.get_argument('drama', '') == 'on':
                    volunteers = volunteers.filter_by(drama=True)
                if self.get_argument('public_school_outreach', '') == 'on':
                    volunteers = volunteers.filter_by(public_school_outreach=True)
                if self.get_argument('retirement_slash_nursing_home_outreach', '') == 'on':
                    volunteers = volunteers.filter_by(retirement_slash_nursing_home_outreach=True)
                if self.get_argument('helping_the_homeless_slash_disadvantaged', '') == 'on':
                    volunteers = volunteers.filter_by(helping_the_homeless_slash_disadvantaged=True)
                if self.get_argument('working_with_youth', '') == 'on':
                    volunteers = volunteers.filter_by(working_with_youth=True)
                if self.get_argument('working_with_children', '') == 'on':
                    volunteers = volunteers.filter_by(working_with_children=True)
                if self.get_argument('greeting', '') == 'on':
                    volunteers = volunteers.filter_by(greeting=True)
                if self.get_argument('shofar_for_vespers', '') == 'on':
                    volunteers = volunteers.filter_by(shofar_for_vespers=True)
                if self.get_argument('music', '') != '':
                    volunteers = volunteers.filter(Volunteer.music.ilike('%'+str(self.get_argument('music',''))+'%'))
                if self.get_argument('join_small_groups', '') == 'on':
                    volunteers = volunteers.filter_by(join_small_groups=True)
                if self.get_argument('lead_small_groups', '') == 'on':
                    volunteers = volunteers.filter_by(lead_small_groups=True)
                if self.get_argument('can_transport_things', '') == 'on':
                    volunteers = volunteers.filter_by(can_transport_things=True)
                if self.get_argument('languages', '') != '':
                    volunteers = volunteers.filter(Volunteer.languages.ilike('%'+str(self.get_argument('languages',''))+'%'))
                if self.get_argument('wants_to_be_involved', '') == 'on':
                    volunteers = volunteers.filter_by(wants_to_be_involved=True)

                vusers = [{'profile': query_by_wwuid(Profile, v.wwuid)[0], 'volunteer_data': v} for v in volunteers]
                if cmd == 'search':
                    self.write({'results': [{'full_name': v['profile'].full_name, 'email': v['profile'].email} for v in vusers]})
                else:
                    logger.debug(user)
                    self.write('<table border="1"><tr><th>Photo</th><th>Name</th><th>Class Standing</th><th>Major(s)</th><th>Email</th><th>Phone</th><th>Volunteer Data</th></tr>')
                    for v in vusers:
                        self.write('<tr><td>'+('<img src="https://aswwu.com/media/img-xs/'+str(v['profile'].photo)+'">' if str(v['profile'].photo).find(str(v['profile'].wwuid)) > -1 else '')+'</td>'\
                                    '<td>'+str(v['profile'].full_name)+'</td>''<td>'+str(v['profile'].class_standing)+'</td><td>'+str(v['profile'].majors)+'</td>'\
                                    '<td>'+str(v['profile'].email)+'</td>''<td>'+str(v['profile'].phone)+'</td><td>'+str(v['volunteer_data'].only_true())+'</td></tr>')
                    self.write('</table>')

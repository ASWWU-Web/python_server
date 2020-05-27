import json
import logging

import tornado.web

from src.aswwu.base_handlers import BaseHandler
import src.aswwu.models.mask as mask_model
import src.aswwu.models.volunteers as volunteer_model
import src.aswwu.alchemy_new.mask as alchemy
from settings import environment

logger = logging.getLogger(environment["log_name"])


# fairly straightforward handler to save a TON of volunteer information
class VolunteerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, wwuid):
        user = self.current_user
        if user.wwuid == wwuid or 'volunteer' in user.roles:
            volunteer = alchemy.query_by_wwuid(volunteer_model.Volunteer, wwuid)
            if len(volunteer) == 0:
                volunteer = volunteer_model.Volunteer(wwuid=user.wwuid)
                volunteer = alchemy.add_or_update(volunteer)
            else:
                volunteer = volunteer[0]
            self.write(volunteer.to_json())
        else:
            self.write({'error': 'insufficient permissions'})

    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        volunteer = alchemy.query_by_wwuid(volunteer_model.Volunteer, user.wwuid)[0]

        volunteer.campus_ministries = (True if self.get_argument('campus_ministries', 0) == '1' else False)
        volunteer.student_missions = (True if self.get_argument('student_missions', 0) == '1' else False)
        volunteer.aswwu = (True if self.get_argument('aswwu', 0) == '1' else False)
        volunteer.circle_church = (True if self.get_argument('circle_church', 0) == '1' else False)
        volunteer.university_church = (True if self.get_argument('university_church', 0) == '1' else False)
        volunteer.buddy_program = (True if self.get_argument('buddy_program', 0) == '1' else False)
        volunteer.assist = (True if self.get_argument('assist', 0) == '1' else False)
        volunteer.lead = (True if self.get_argument('lead', 0) == '1' else False)
        volunteer.audio_slash_visual = (True if self.get_argument('audio_slash_visual', 0) == '1' else False)
        volunteer.health_promotion = (True if self.get_argument('health_promotion', 0) == '1' else False)
        volunteer.construction_experience = (True if self.get_argument('construction_experience', 0) == '1' else False)
        volunteer.outdoor_slash_camping = (True if self.get_argument('outdoor_slash_camping', 0) == '1' else False)
        volunteer.concert_assistance = (True if self.get_argument('concert_assistance', 0) == '1' else False)
        volunteer.event_set_up = (True if self.get_argument('event_set_up', 0) == '1' else False)
        volunteer.children_ministries = (True if self.get_argument('children_ministries', 0) == '1' else False)
        volunteer.children_story = (True if self.get_argument('children_story', 0) == '1' else False)
        volunteer.art_poetry_slash_painting_slash_sculpting = \
            (True if self.get_argument('art_poetry_slash_painting_slash_sculpting', 0) == '1' else False)
        volunteer.organizing_events = (True if self.get_argument('organizing_events', 0) == '1' else False)
        volunteer.organizing_worship_opportunities = \
            (True if self.get_argument('organizing_worship_opportunities', 0) == '1' else False)
        volunteer.organizing_community_outreach = \
            (True if self.get_argument('organizing_community_outreach', 0) == '1' else False)
        volunteer.bible_study = (True if self.get_argument('bible_study', 0) == '1' else False)
        volunteer.wycliffe_bible_translator_representative = \
            (True if self.get_argument('wycliffe_bible_translator_representative', 0) == '1' else False)
        volunteer.food_preparation = (True if self.get_argument('food_preparation', 0) == '1' else False)
        volunteer.graphic_design = (True if self.get_argument('graphic_design', 0) == '1' else False)
        volunteer.poems_slash_spoken_word = (True if self.get_argument('poems_slash_spoken_word', 0) == '1' else False)
        volunteer.prayer_team_slash_prayer_house = \
            (True if self.get_argument('prayer_team_slash_prayer_house', 0) == '1' else False)
        volunteer.dorm_encouragement_and_assisting_chaplains = \
            (True if self.get_argument('dorm_encouragement_and_assisting_chaplains', 0) == '1' else False)
        volunteer.scripture_reading = (True if self.get_argument('scripture_reading', 0) == '1' else False)
        volunteer.speaking = (True if self.get_argument('speaking', 0) == '1' else False)
        volunteer.videography = (True if self.get_argument('videography', 0) == '1' else False)
        volunteer.drama = (True if self.get_argument('drama', 0) == '1' else False)
        volunteer.public_school_outreach = (True if self.get_argument('public_school_outreach', 0) == '1' else False)
        volunteer.retirement_slash_nursing_home_outreach = \
            (True if self.get_argument('retirement_slash_nursing_home_outreach', 0) == '1' else False)
        volunteer.helping_the_homeless_slash_disadvantaged = \
            (True if self.get_argument('helping_the_homeless_slash_disadvantaged', 0) == '1' else False)
        volunteer.working_with_youth = (True if self.get_argument('working_with_youth', 0) == '1' else False)
        volunteer.working_with_children = (True if self.get_argument('working_with_children', 0) == '1' else False)
        volunteer.greeting = (True if self.get_argument('greeting', 0) == '1' else False)
        volunteer.shofar_for_vespers = (True if self.get_argument('shofar_for_vespers', 0) == '1' else False)
        volunteer.music = self.get_argument('music', '')
        volunteer.join_small_groups = (True if self.get_argument('join_small_groups', 0) == '1' else False)
        volunteer.lead_small_groups = (True if self.get_argument('lead_small_groups', 0) == '1' else False)
        volunteer.can_transport_things = (True if self.get_argument('can_transport_things', 0) == '1' else False)
        volunteer.languages = self.get_argument('languages', '')
        volunteer.berean_fellowship = self.get_argument('berean_fellowship', '')
        volunteer.aswwu_video_extra = self.get_argument('aswwu_video_extra', '')
        volunteer.global_service_food_fair = self.get_argument('global_service_food_fair', '')
        volunteer.wants_to_be_involved = (True if self.get_argument('wants_to_be_involved', 0) == '1' else False)

        logger.debug(volunteer.only_true())
        alchemy.add_or_update(volunteer)
        self.write(json.dumps('success'))


# handler to search through volunteer information
class VolunteerRoleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        # check permissions
        if 'volunteer' not in user.roles:
            self.write({'error': 'insufficient permissions'})
        else:
            cmd = self.get_argument('cmd', None)
            logger.debug(cmd)
            if cmd == 'set_role':
                # let volunteer admins grant permissions for other volutneer admins
                username = self.get_argument('username', '').replace(' ', '.').lower()
                # .ilike is for case insesitive.
                fuser = alchemy.people_db.query(mask_model.User).filter(mask_model.User.username.ilike(username)).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    if fuser.roles is None:
                        fuser.roles = ''
                    roles = fuser.roles.split(',')
                    roles.append('volunteer')
                    roles = set(roles)
                    fuser.roles = ','.join(roles)
                    alchemy.add_or_update(fuser)
                    self.write({'response': 'success'})
            elif cmd == 'search' or cmd == 'viewPrintOut':
                # searcheth away!
                volunteers = alchemy.people_db.query(volunteer_model.Volunteer)
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
                    volunteers = volunteers.filter(
                        volunteer_model.Volunteer.music.ilike('%'+str(self.get_argument('music', ''))+'%')
                    )
                if self.get_argument('join_small_groups', '') == 'on':
                    volunteers = volunteers.filter_by(join_small_groups=True)
                if self.get_argument('lead_small_groups', '') == 'on':
                    volunteers = volunteers.filter_by(lead_small_groups=True)
                if self.get_argument('can_transport_things', '') == 'on':
                    volunteers = volunteers.filter_by(can_transport_things=True)
                if self.get_argument('languages', '') != '':
                    volunteers = volunteers.filter(
                        volunteer_model.Volunteer.languages.ilike('%'+str(self.get_argument('languages', ''))+'%')
                    )
                if self.get_argument('berean_fellowship', '') != '':
                    volunteers = volunteers.filter_by(berean_fellowship=True)
                if self.get_argument('aswwu_video_extra', '') != '':
                    volunteers = volunteers.filter_by(aswwu_video_extra=True)
                if self.get_argument('global_service_food_fair', '') != '':
                    volunteers = volunteers.filter_by(global_service_food_fair=True)
                if self.get_argument('wants_to_be_involved', '') == 'on':
                    volunteers = volunteers.filter_by(wants_to_be_involved=True)

                # vusers = [{'profile': query_by_wwuid(Profile, v.wwuid)[0], 'volunteer_data': v} for v in volunteers]
                vusers = []
                for v in volunteers:
                    vol_result = alchemy.query_by_wwuid(mask_model.Profile, v.wwuid)
                    if len(vol_result) > 0:
                        vusers.append({'profile': vol_result[0], 'volunteer_data': v})
                # should we return the results as JSON
                if cmd == 'search':
                    self.write({'results': [{'full_name': v['profile'].full_name, 'email': v['profile'].email,
                                             'photo': v['profile'].photo,
                                             'username': v['profile'].username} for v in vusers]})
                # or as a full fledged webpage
                else:
                    logger.debug(user)
                    self.write('<table border="1"><tr>'
                               '<th>Photo</th><th>Name</th>'
                               '<th>Class Standing</th><th>Major(s)</th>'
                               '<th>Email</th><th>Phone</th>'
                               '<th>Volunteer Data</th></tr>')
                    for v in vusers:
                        self.write('<tr><td>' + ('<img src="https://aswwu.com/media/img-xs/'
                                                 + str(v['profile'].photo)+'">'
                                                 if str(v['profile'].photo).find(str(v['profile'].wwuid)) > -1 else '')
                                   + '</td><td>' + str(v['profile'].full_name) + '</td>''<td>'
                                   + str(v['profile'].class_standing) + '</td><td>' + str(v['profile'].majors)
                                   + '</td><td>' + str(v['profile'].email) + '</td>''<td>' + str(v['profile'].phone)
                                   + '</td><td>' + str(v['volunteer_data'].only_true()) + '</td></tr>')
                    self.write('</table>')

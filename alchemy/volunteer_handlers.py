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


class VolunteerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, wwuid):
        user = self.current_user
        if user.wwuid == wwuid or 'volunteer' in user.roles:
            volunteer = query_by_wwuid(Volunteer, wwuid)
            if len(volunteer) == 0:
                volunteer = Volunteer(wwuid=user.wwuid)
                volunteer = addOrUpdate(volunteer)
            else:
                volunteer = volunteer[0]
            self.write(volunteer.to_json())
        else:
            self.write({'error': 'insufficient permissions'})

    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        volunteer = query_by_wwuid(Volunteer, user.wwuid)[0]

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
        volunteer.art_poetry_slash_painting_slash_sculpting = (True if self.get_argument('art_poetry_slash_painting_slash_sculpting', 0) == '1' else False)
        volunteer.organizing_events = (True if self.get_argument('organizing_events', 0) == '1' else False)
        volunteer.organizing_worship_opportunities = (True if self.get_argument('organizing_worship_opportunities', 0) == '1' else False)
        volunteer.organizing_community_outreach = (True if self.get_argument('organizing_community_outreach', 0) == '1' else False)
        volunteer.bible_study = (True if self.get_argument('bible_study', 0) == '1' else False)
        volunteer.wycliffe_bible_translator_representative = (True if self.get_argument('wycliffe_bible_translator_representative', 0) == '1' else False)
        volunteer.food_preparation = (True if self.get_argument('food_preparation', 0) == '1' else False)
        volunteer.graphic_design = (True if self.get_argument('graphic_design', 0) == '1' else False)
        volunteer.poems_slash_spoken_word = (True if self.get_argument('poems_slash_spoken_word', 0) == '1' else False)
        volunteer.prayer_team_slash_prayer_house = (True if self.get_argument('prayer_team_slash_prayer_house', 0) == '1' else False)
        volunteer.dorm_encouragement_and_assisting_chaplains = (True if self.get_argument('dorm_encouragement_and_assisting_chaplains', 0) == '1' else False)
        volunteer.scripture_reading = (True if self.get_argument('scripture_reading', 0) == '1' else False)
        volunteer.speaking = (True if self.get_argument('speaking', 0) == '1' else False)
        volunteer.videography = (True if self.get_argument('videography', 0) == '1' else False)
        volunteer.drama = (True if self.get_argument('drama', 0) == '1' else False)
        volunteer.public_school_outreach = (True if self.get_argument('public_school_outreach', 0) == '1' else False)
        volunteer.retirement_slash_nursing_home_outreach = (True if self.get_argument('retirement_slash_nursing_home_outreach', 0) == '1' else False)
        volunteer.helping_the_homeless_slash_disadvantaged = (True if self.get_argument('helping_the_homeless_slash_disadvantaged', 0) == '1' else False)
        volunteer.working_with_youth = (True if self.get_argument('working_with_youth', 0) == '1' else False)
        volunteer.working_with_children = (True if self.get_argument('working_with_children', 0) == '1' else False)
        volunteer.greeting = (True if self.get_argument('greeting', 0) == '1' else False)
        volunteer.shofar_for_vespers = (True if self.get_argument('shofar_for_vespers', 0) == '1' else False)
        volunteer.music = self.get_argument('music', '')
        volunteer.join_small_groups = (True if self.get_argument('join_small_groups', 0) == '1' else False)
        volunteer.lead_small_groups = (True if self.get_argument('lead_small_groups', 0) == '1' else False)
        volunteer.can_transport_things = (True if self.get_argument('can_transport_things', 0) == '1' else False)
        volunteer.languages = self.get_argument('languages', '')
        volunteer.wants_to_be_involved = (True if self.get_argument('wants_to_be_involved', 0) == '1' else False)

        logger.debug(volunteer.only_true())
        addOrUpdate(volunteer)
        self.write(json.dumps('success'))

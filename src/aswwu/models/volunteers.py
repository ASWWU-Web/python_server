import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base

import src.aswwu.models.bases as base

Base = declarative_base(cls=base.Base)


# an unfortunately large table to hold the volunteer information
# NOTE: this should and could probably be stored as a JSON blob
class Volunteer(Base):
    __tablename__ = 'volunteers'

    wwuid = Column(String(7), ForeignKey('users.wwuid'), nullable=False)
    campus_ministries = Column(Boolean, default=False)
    student_missions = Column(Boolean, default=False)
    aswwu = Column(Boolean, default=False)
    circle_church = Column(Boolean, default=False)
    university_church = Column(Boolean, default=False)
    buddy_program = Column(Boolean, default=False)
    assist = Column(Boolean, default=False)
    lead = Column(Boolean, default=False)
    audio_slash_visual = Column(Boolean, default=False)
    health_promotion = Column(Boolean, default=False)
    construction_experience = Column(Boolean, default=False)
    outdoor_slash_camping = Column(Boolean, default=False)
    concert_assistance = Column(Boolean, default=False)
    event_set_up = Column(Boolean, default=False)
    children_ministries = Column(Boolean, default=False)
    children_story = Column(Boolean, default=False)
    art_poetry_slash_painting_slash_sculpting = Column(Boolean, default=False)
    organizing_events = Column(Boolean, default=False)
    organizing_worship_opportunities = Column(Boolean, default=False)
    organizing_community_outreach = Column(Boolean, default=False)
    bible_study = Column(Boolean, default=False)
    wycliffe_bible_translator_representative = Column(Boolean, default=False)
    food_preparation = Column(Boolean, default=False)
    graphic_design = Column(Boolean, default=False)
    poems_slash_spoken_word = Column(Boolean, default=False)
    prayer_team_slash_prayer_house = Column(Boolean, default=False)
    dorm_encouragement_and_assisting_chaplains = Column(Boolean, default=False)
    scripture_reading = Column(Boolean, default=False)
    speaking = Column(Boolean, default=False)
    videography = Column(Boolean, default=False)
    drama = Column(Boolean, default=False)
    public_school_outreach = Column(Boolean, default=False)
    retirement_slash_nursing_home_outreach = Column(Boolean, default=False)
    helping_the_homeless_slash_disadvantaged = Column(Boolean, default=False)
    working_with_youth = Column(Boolean, default=False)
    working_with_children = Column(Boolean, default=False)
    greeting = Column(Boolean, default=False)
    shofar_for_vespers = Column(Boolean, default=False)
    music = Column(String(250), default=False)
    join_small_groups = Column(Boolean, default=False)
    lead_small_groups = Column(Boolean, default=False)
    can_transport_things = Column(Boolean, default=False)
    languages = Column(String(250), default=False)
    wants_to_be_involved = Column(Boolean, default=False)
    berean_fellowship = Column(Boolean, default=False)
    aswwu_video_extra = Column(Boolean, default=False)
    global_service_food_fair = Column(Boolean, default=False)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    # for easier admin searching, show only the fields that aren't false or blank
    def only_true(self):
        fields = ['campus_ministries', 'student_missions', 'aswwu', 'circle_church', 'university_church', 'assist',
                  'lead', 'audio_slash_visual', 'health_promotion', 'construction_experience', 'outdoor_slash_camping',
                  'concert_assistance', 'event_set_up', 'children_ministries', 'children_story',
                  'art_poetry_slash_painting_slash_sculpting', 'organizing_events', 'organizing_worship_opportunities',
                  'organizing_community_outreach', 'bible_study', 'wycliffe_bible_translator_representative',
                  'food_preparation', 'graphic_design', 'poems_slash_spoken_word', 'prayer_team_slash_prayer_house',
                  'dorm_encouragement_and_assisting_chaplains', 'scripture_reading', 'speaking', 'videography',
                  'drama', 'public_school_outreach', 'retirement_slash_nursing_home_outreach',
                  'helping_the_homeless_slash_disadvantaged', 'working_with_youth', 'working_with_children',
                  'greeting', 'shofar_for_vespers', 'music', 'join_small_groups', 'lead_small_groups',
                  'can_transport_things', 'languages', 'berean_fellowship', 'aswwu_video_extra',
                  'global_service_food_fair', 'wants_to_be_involved']
        data = []
        for f in fields:
            if getattr(self, f):
                data.append(str(f))
            elif getattr(self, f) != '':
                if f == 'music':
                    data.append({'music': self.music})
                elif f == 'languages':
                    data.append({'languages': self.languages})
        return data

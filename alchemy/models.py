from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
import uuid
import datetime
from sqlalchemy.ext.declarative import declarative_base
import hashlib

Base = declarative_base()

def uuid_gen():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = 'users'
    wwuid = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    full_name = Column(String(250))
    status = Column(String(250))
    roles = Column(String(500))
    def to_json(self):
        return {'wwuid': str(self.wwuid), 'username': str(self.username), 'full_name': str(self.full_name), 'status': str(self.status), 'roles': str(self.roles)}

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(String(50), primary_key=True, default=uuid_gen)
    wwuid = Column(Integer, ForeignKey('users.wwuid'), nullable=False)
    auth_salt = Column(String(250), default=uuid_gen)
    auth_time = Column(DateTime, default=datetime.datetime.now)
    def __repr__(self):
        t = hashlib.sha512(str(self.wwuid)+str(self.auth_salt)).hexdigest()
        return str(self.id)+'|'+str(self.wwuid)+'|'+str(t)

class Message(Base):
    __tablename__ = 'messaages'
    id = Column(String(50), primary_key=True, default=uuid_gen)
    sender = Column(Integer, ForeignKey('users.wwuid'))
    receiver = Column(Integer, ForeignKey('users.wwuid'))
    message = Column(String(1000))
    created_at = Column(DateTime, default=datetime.datetime.now)
    read_at = Column(DateTime, onupdate=datetime.datetime.now)


class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(String(50), primary_key=True, default=uuid_gen)
    wwuid = Column(Integer, ForeignKey('users.wwuid'), nullable=False)
    username = Column(String(250))
    full_name = Column(String(250))
    photo = Column(String(250))
    gender = Column(String(250))
    birthday = Column(String(250))
    email = Column(String(250))
    phone = Column(String(250))
    website = Column(String(250))
    majors = Column(String(500))
    minors = Column(String(500))
    graduate = Column(String(250))
    preprofessional = Column(String(250))
    class_standing = Column(String(250))
    relationship_status = Column(String(250))
    attached_to = Column(String(250))
    quote = Column(String(1000))
    quote_author = Column(String(250))
    hobbies = Column(String(500))
    career_goals = Column(String(1000))
    favorite_books = Column(String(1000))
    favorite_food = Column(String(1000))
    favorite_movies = Column(String(1000))
    favorite_music = Column(String(1000))
    pet_peeves = Column(String(500))
    personality = Column(String(250))
    views = Column(Integer)
    privacy = Column(Integer)
    department = Column(String(250))
    office = Column(String(250))
    office_hours = Column(String(250))
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)


class Volunteer(Base):
    __tablename__ = 'volunteers'
    id = Column(String(50), primary_key=True, default=uuid_gen)
    wwuid = Column(Integer, ForeignKey('users.wwuid'), nullable=False)
    campus_ministries = Column(Boolean, default=False)
    student_missions = Column(Boolean, default=False)
    aswwu = Column(Boolean, default=False)
    circle_church = Column(Boolean, default=False)
    university_church = Column(Boolean, default=False)
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
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

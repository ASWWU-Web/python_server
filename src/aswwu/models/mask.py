from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, backref

import src.aswwu.models.bases as base

Base = declarative_base(cls=base.Base)


# you guessed it, our generic User model
class User(Base):
    __tablename__ = 'users'

    wwuid = Column(String(7), unique=True)
    username = Column(String(250), nullable=False)
    full_name = Column(String(250))
    status = Column(String(250))
    roles = Column(String(500))


# table for profile data
class Profile(Base):
    __tablename__ = 'profiles'

    wwuid = Column(String(7), ForeignKey('users.wwuid'), nullable=False)
    username = Column(String(250), CheckConstraint('LENGTH(username) < 250'))
    full_name = Column(String(250), CheckConstraint('LENGTH(full_name) < 250'))
    photo = Column(String(250))
    gender = Column(String(250))
    birthday = Column(String(250))
    email = Column(String(250), CheckConstraint('LENGTH(email) < 250'))
    phone = Column(String(250), CheckConstraint('LENGTH(phone) < 250'))
    website = Column(String(250))
    majors = Column(String(500))
    minors = Column(String(500))
    graduate = Column(String(250))
    preprofessional = Column(String(250))
    class_standing = Column(String(250))
    high_school = Column(String(250))
    class_of = Column(String(250))
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
    # DEPRECATED
    views = relationship("ProfileView", backref=backref("profile", uselist=False), lazy="dynamic")
    privacy = Column(Integer)
    department = Column(String(250))
    office = Column(String(250))
    office_hours = Column(String(250))

    # sometimes useful to only get a small amount of information about a user
    # e.g. listing ALL of the profiles in a cache for faster search later
    def base_info(self):
        return self.to_json(limitList=['username', 'full_name', 'photo', 'email'])

    def impers_info(self):
        return self.to_json(limitList=['username', 'full_name', 'photo', 'gender', 'website', 'majors', 'minors',
                                       'graduate', 'preprofessional', 'relationship_status', 'quote', 'quote_author',
                                       'hobbies', 'career_goals', 'favorite_books', 'favorite_movies',
                                       'favorite_music', 'pet_peeves', 'personality',
                                       'privacy', 'department', 'office', 'office_hours'])

    def view_other(self):
        return self.to_json(limitList=['username', 'full_name', 'photo', 'gender', 'birthday', 'email', 'phone',
                                       'website', 'majors', 'minors', 'graduate', 'preprofessional', 'class_standing',
                                       'high_school', 'class_of', 'relationship_status', 'attached_to', 'quote',
                                       'quote_author', 'hobbies', 'career_goals', 'favorite_books', 'favorite_movies',
                                       'favorite_music', 'pet_peeves', 'personality', 'privacy',
                                       'department', 'office', 'office_hours'])

class ProfileView(Base):
    __tablename__ = 'profileviews'

    viewer = Column(String(75), ForeignKey('users.username'), nullable=False)
    viewed = Column(String(75), ForeignKey('profiles.username'), nullable=False)
    last_viewed = Column(DateTime)
    num_views = Column(Integer, default=0, index=True)

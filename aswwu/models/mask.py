from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import relationship, backref

from aswwu.models.bases import MaskBase


# you guessed it, our generic User model
class User(MaskBase):
    wwuid = Column(String(7), unique=True)
    username = Column(String(250), nullable=False, unique=True)
    full_name = Column(String(250))
    status = Column(String(250))
    roles = Column(String(500))

    def serialize(self):
        return {
            'wwuid': self.wwuid,
            'username': self.username,
            'full_name': self.full_name,
            'status': self.status,
            'roles': self.roles
        }


# table for profile data
class Profile(MaskBase):
    wwuid = Column(String(7), ForeignKey('mask_users.wwuid'), nullable=False)
    username = Column(String(250), CheckConstraint('LENGTH(username) < 250'), unique=True)
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
    quote = Column(String(3000))
    quote_author = Column(String(250))
    hobbies = Column(String(500))
    career_goals = Column(String(1000))
    favorite_books = Column(String(1000))
    favorite_food = Column(String(1000))
    favorite_movies = Column(String(1000))
    favorite_music = Column(String(1000))
    pet_peeves = Column(String(500))
    personality = Column(String(250))
    # views = relationship("ProfileView", backref=backref("profile", uselist=False), lazy="dynamic")
    views = Column(Integer, default=0)
    privacy = Column(Integer)
    department = Column(String(250))
    office = Column(String(250))
    office_hours = Column(String(250))

    def num_views(self):
        return self.views

    def serialize(self):
        return {
            'wwuid': self.wwuid,
            'username': self.username,
            'full_name': self.full_name,
            'photo': self.photo,
            'gender': self.gender,
            'birthday': self.birthday,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'majors': self.majors,
            'minors': self.minors,
            'graduate': self.graduate,
            'preprofessional': self.preprofessional,
            'class_standing': self.class_standing,
            'high_school': self.high_school,
            'class_of': self.class_of,
            'relationship_status': self.relationship_status,
            'attached_to': self.attached_to,
            'quote': self.quote,
            'quote_author': self.quote_author,
            'hobbies': self.hobbies,
            'career_goals': self.career_goals,
            'favorite_books': self.favorite_books,
            'favorite_food': self.favorite_food,
            'favorite_movies': self.favorite_movies,
            'favorite_music': self.favorite_music,
            'pet_peeves': self.pet_peeves,
            'personality': self.personality,
            'views': self.views,
            'privacy': self.privacy,
            'department': self.department,
            'office': self.office,
            'office_hours': self.office_hours
        }

    def serialize_no_wwuid(self):
        profile = self.serialize()
        del profile['wwuid']
        return profile

    def serialize_summary(self):
        return {
            'username': self.username,
            'full_name': self.full_name,
            'photo': self.photo,
            'email': self.email,
            'views': self.views
        }


class ProfileView(MaskBase):
    viewer = Column(String(75), ForeignKey('mask_users.username'), nullable=False)
    viewed = Column(String(75), ForeignKey('mask_profiles.username'), nullable=False)
    last_viewed = Column(DateTime)
    num_views = Column(Integer, default=0, index=True)

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, CheckConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import Mapped, mapped_column

from src.aswwu.models.bases import Base

# you guessed it, our generic User model
class User(Base):
    __tablename__ = 'users'

    wwuid: Mapped[str] = mapped_column(String(7), unique=True)
    username: Mapped[str] = mapped_column(String(250), nullable=False)
    full_name: Mapped[str] = mapped_column(String(250))
    status: Mapped[str] = mapped_column(String(250))
    roles: Mapped[str] = mapped_column(String(500))

class ProfileView(Base):
    __tablename__ = 'profileviews'

    viewer = Column(String(75), ForeignKey('users.username'), nullable=False)
    viewed = Column(String(75), ForeignKey('profiles.username'), nullable=False)
    last_viewed = Column(DateTime)
    num_views = Column(Integer, default=0, index=True)

# table for profile data
class Profile(Base):
    __tablename__ = 'profiles'

    wwuid: Mapped[str] = mapped_column(String(7), ForeignKey('users.wwuid'), nullable=False)
    username: Mapped[str] = mapped_column(String(250), CheckConstraint('LENGTH(username) < 250'))
    full_name: Mapped[str] = mapped_column(String(250), CheckConstraint('LENGTH(full_name) < 250'))
    photo: Mapped[str] = mapped_column(String(250), default='assets/mask/default.jpg')
    gender: Mapped[str] = mapped_column(String(250), default='')
    birthday: Mapped[str] = mapped_column(String(250), default='')
    email: Mapped[str] = mapped_column(String(250), CheckConstraint('LENGTH(email) < 250'), default='')
    phone: Mapped[str] = mapped_column(String(250), CheckConstraint('LENGTH(phone) < 250'), default='')
    website: Mapped[str] = mapped_column(String(250), default='')
    majors: Mapped[str] = mapped_column(String(500), default='')
    minors: Mapped[str] = mapped_column(String(500), default='')
    graduate: Mapped[str] = mapped_column(String(250), default='')
    preprofessional: Mapped[str] = mapped_column(String(250), default='')
    class_standing: Mapped[str] = mapped_column(String(250), default='')
    high_school: Mapped[str] = mapped_column(String(250), default='')
    class_of: Mapped[str] = mapped_column(String(250), default='')
    relationship_status: Mapped[str] = mapped_column(String(250), default='')
    attached_to: Mapped[str] = mapped_column(String(250), default='')
    quote: Mapped[str] = mapped_column(String(1000), default='')
    quote_author: Mapped[str] = mapped_column(String(250), default='')
    hobbies: Mapped[str] = mapped_column(String(500), default='')
    career_goals: Mapped[str] = mapped_column(String(1000), default='')
    favorite_books: Mapped[str] = mapped_column(String(1000), default='')
    favorite_food: Mapped[str] = mapped_column(String(1000), default='')
    favorite_movies: Mapped[str] = mapped_column(String(1000), default='')
    favorite_music: Mapped[str] = mapped_column(String(1000), default='')
    pet_peeves: Mapped[str] = mapped_column(String(500), default='')
    personality: Mapped[str] = mapped_column(String(250), default='')
    # DEPRECATED
    views = relationship("ProfileView", backref=backref("profile", uselist=False), lazy="dynamic")
    privacy: Mapped[int] = mapped_column(Integer, CheckConstraint('privacy >= 0 AND privacy <= 1'), default=0)
    department: Mapped[str] = mapped_column(String(250))
    office: Mapped[str] = mapped_column(String(250))
    office_hours: Mapped[str] = mapped_column(String(250))

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

    



# this file defines individual models for each of the previous years
# at this point the fields have all been standardized
# each year just add another model class and add the year's shorthand (i.e. 1415) to the array at the bottom

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from alchemy.setup import ArchiveBase

def setArchiveColumns(self):
    self.wwuid = Column(Integer, nullable=False)
    self.username = Column(String(250))
    self.full_name = Column(String(250))
    self.photo = Column(String(250))
    self.gender = Column(String(250))
    self.birthday = Column(String(250))
    self.email = Column(String(250))
    self.phone = Column(String(250))
    self.website = Column(String(250))
    self.majors = Column(String(500))
    self.minors = Column(String(500))
    self.graduate = Column(String(250))
    self.preprofessional = Column(String(250))
    self.class_standing = Column(String(250))
    self.high_school = Column(String(250))
    self.class_of = Column(String(250))
    self.relationship_status = Column(String(250))
    self.attached_to = Column(String(250))
    self.quote = Column(String(1000))
    self.quote_author = Column(String(250))
    self.hobbies = Column(String(500))
    self.career_goals = Column(String(1000))
    self.favorite_books = Column(String(1000))
    self.favorite_food = Column(String(1000))
    self.favorite_movies = Column(String(1000))
    self.favorite_music = Column(String(1000))
    self.pet_peeves = Column(String(500))
    self.personality = Column(String(250))
    self.views = Column(Integer)
    self.privacy = Column(Integer)
    self.department = Column(String(250))
    self.office = Column(String(250))
    self.office_hours = Column(String(250))
    def to_json(self):
        return {'wwuid': str(self.wwuid), 'username': str(self.username), 'full_name': str(self.full_name), 'photo': str(self.photo),\
                'gender': str(self.gender), 'birthday': str(self.birthday), 'email': str(self.email), 'phone': str(self.phone), 'website': str(self.website),\
                'majors': str(self.majors), 'minors': str(self.minors), 'graduate': str(self.graduate), 'preprofessional': str(self.preprofessional),\
                'class_standing': str(self.class_standing), 'high_school': str(self.high_school), 'class_of': str(self.class_of),
                'relationship_status': str(self.relationship_status), 'attached_to': str(self.attached_to), 'quote': str(self.quote), 'quote_author': str(self.quote_author),\
                'hobbies': str(self.hobbies), 'career_goals': str(self.career_goals), 'favorite_books': str(self.favorite_books), 'favorite_food': str(self.favorite_food),\
                'favorite_movies': str(self.favorite_movies), 'favorite_music': str(self.favorite_music), 'pet_peeves': str(self.pet_peeves), 'personality': str(self.personality),\
                'views': str(self.views), 'department': str(self.department), 'office': str(self.office), 'office_hours': str(self.office_hours)}
    def base_info(self):
        return {'username': str(self.username), 'full_name': str(self.full_name), 'photo': str(self.photo), 'views': str(self.views)}
    self.to_json = to_json
    self.base_info = base_info

class Archive1415(ArchiveBase):
    __tablename__ = 'profiles1415'
    id = Column(String(50), primary_key=True)

class Archive1314(ArchiveBase):
    __tablename__ = 'profiles1314'
    id = Column(String(50), primary_key=True)

class Archive1213(ArchiveBase):
    __tablename__ = 'profiles1213'
    id = Column(String(50), primary_key=True)

class Archive1112(ArchiveBase):
    __tablename__ = 'profiles1112'
    id = Column(String(50), primary_key=True)

class Archive1011(ArchiveBase):
    __tablename__ = 'profiles1011'
    id = Column(String(50), primary_key=True)

class Archive0910(ArchiveBase):
    __tablename__ = 'profiles0910'
    id = Column(String(50), primary_key=True)

class Archive0809(ArchiveBase):
    __tablename__ = 'profiles0809'
    id = Column(String(50), primary_key=True)

class Archive0708(ArchiveBase):
    __tablename__ = 'profiles0708'
    id = Column(String(50), primary_key=True)

class Archive0607(ArchiveBase):
    __tablename__ = 'profiles0607'
    id = Column(String(50), primary_key=True)

for y in ["1415","1314","1213","1112","1011","0910","0809","0708","0607"]:
    setArchiveColumns(globals()["Archive"+y])

# archive_models.py

# this file defines individual models for each of the previous years
# at this point the fields have all been standardized
# each year just add another model class and add the year's shorthand (i.e. 1415) to the array at the bottom

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


# define a base model for the Archives
class ArchiveBase(object):
    # a useful function is being able to call `model.to_json()` and getting valid JSON to send to the user
    def to_json(self, **kwargs):
        obj = {}
        # get the column names of the table
        columns = [str(key).split(".")[1] for key in self.__table__.columns]
        # if called with `model.to_json(skipList=["something"])`
        # then "something" will be added to the list of columns to skip
        skip_list = ['id'] + kwargs.get('skip_list', [])
        # if called similarly to skipList, then only those columns will even be checked
        # by default we check all of the table's columns
        limit_list = kwargs.get('limitList', columns)
        for key in limit_list:
            if key not in skip_list:
                # fancy way of saying "self.key"
                value = getattr(self, key)
                # try to set the value as a string, but that doesn't always work
                # NOTE: this should be encoded more properly sometime
                try:
                    obj[key] = str(value)
                except:
                    pass
        return obj

    def base_info(self):
        return self.to_json(limitList=['username', 'full_name', 'photo', 'email', 'views'])
    # TODO: remove email from base_info

    def no_info(self):
        return self.to_json(limitList=['username', 'full_name', 'photo', 'views', 'privacy'])

    def impers_info(self):
        return self.to_json(limitList=['username', 'full_name', 'photo', 'gender', 'website', 'majors', 'minors',
                                       'graduate', 'preprofessional', 'relationship_status', 'quote', 'quote_author',
                                       'hobbies', 'career_goals', 'favorite_books', 'favorite_movies', 'favorite_music',
                                       'pet_peeves', 'personality', 'views', 'privacy', 'department', 'office',
                                       'office_hours'])

    def view_other(self):
        return self.to_json(limitList=['username', 'full_name', 'photo', 'gender', 'birthday', 'email', 'phone',
                                       'website', 'majors', 'minors', 'graduate', 'preprofessional', 'class_standing',
                                       'high_school', 'class_of', 'relationship_status', 'attached_to', 'quote',
                                       'quote_author', 'hobbies', 'career_goals', 'favorite_books', 'favorite_movies',
                                       'favorite_music', 'pet_peeves', 'personality', 'views', 'privacy', 'department',
                                       'office', 'office_hours'])

    def export_info(self):
        return self.to_json(limitList=['photo', 'gender', 'birthday', 'email', 'phone', 'website', 'majors', 'minors',
                                       'graduate', 'preprofessional', 'high_school', 'class_of', 'relationship_status',
                                       'attached_to', 'quote', 'quote_author', 'hobbies', 'career_goals',
                                       'favorite_books', 'favorite_movies', 'favorite_music', 'pet_peeves',
                                       'personality', 'privacy', 'department', 'office', 'office_hours'])


ArchiveBase = declarative_base(cls=ArchiveBase)


def set_archive_columns(self):
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


class Archive1718(ArchiveBase):
    __tablename__ = 'profiles1718'
    id = Column(String(50), primary_key=True)

class Archive1617(ArchiveBase):
    __tablename__ = 'profiles1617'
    id = Column(String(50), primary_key=True)


class Archive1516(ArchiveBase):
    __tablename__ = 'profiles1516'
    id = Column(String(50), primary_key=True)


class Archive1415(ArchiveBase):
    __tablename__ = 'profiles1415'
    id = Column(String(50), primary_key=True)


# FIXME: Projects here and after cannot have a blank query(return internal server error instead of a list of all profiles);
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


def get_archive_model(archive_year):
    return eval("Archive" + str(archive_year))


for year in ["1718","1617", "1516", "1415", "1314", "1213", "1112", "1011", "0910", "0809", "0708", "0607"]:
    set_archive_columns(get_archive_model(year))

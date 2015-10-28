from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

from alchemy.base_models import *

engine = create_engine("sqlite:///data.db")

Base.metadata.create_all(engine)

Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)

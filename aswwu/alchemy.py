# alchemy.py

# import and set up the logging
import ast
import logging

from sqlalchemy import create_engine, func, or_, and_, desc
from sqlalchemy.orm import sessionmaker, joinedload, class_mapper
from sqlalchemy.sql import label

import aswwu.models.bases as base
import aswwu.models.mask as mask_model
import aswwu.models.pages as pages_model
import aswwu.models.elections as election_model
from aswwu.archive_models import ArchiveBase

Base = base.Base
ElectionBase = base.ElectionBase
PagesBase = base.PagesBase
JobsBase = base.JobsBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
engine = create_engine("sqlite:///../databases/people.db")
archive_engine = create_engine("sqlite:///../databases/archives.db")
election_engine = create_engine("sqlite:///../databases/senate_elections.db")
pages_engine = create_engine("sqlite:///../databases/pages.db")
jobs_engine = create_engine("sqlite:///../databases/jobs.db")

# create the model tables if they don't already exist
Base.metadata.create_all(engine)
ElectionBase.metadata.create_all(election_engine)
PagesBase.metadata.create_all(pages_engine)
JobsBase.metadata.create_all(jobs_engine)

# bind instances of the databases to corresponding variables
Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)
people_db = dbs()
# same for archives
ArchiveBase.metadata.bind = archive_engine
archive_dbs = sessionmaker(bind=archive_engine)
archive_db = archive_dbs()
# same for elections
ElectionBase.metadata.bind = election_engine
election_dbs = sessionmaker(bind=election_engine)
election_db = election_dbs()
# same for pages
PagesBase.metadata.bind = pages_engine
pages_dbs = sessionmaker(bind=pages_engine)
page_db = pages_dbs()

# TODO: Figure out the consequences of this mistake
JobsBase.metadata.bind = election_engine
jobs_dbs = sessionmaker(bind=jobs_engine)
jobs_db = jobs_dbs()








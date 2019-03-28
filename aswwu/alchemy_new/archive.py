# archive.py

import logging

from sqlalchemy.orm import sessionmaker

from aswwu.alchemy_new import connection
from aswwu.archive_models import ArchiveBase

logger = logging.getLogger("aswwu")

# bind instances of the databases to corresponding variables
ArchiveBase.metadata.bind = connection
archive_dbs = sessionmaker(bind=connection)
archive_db = archive_dbs()

# create the model tables if they don't already exist
ArchiveBase.metadata.create_all()

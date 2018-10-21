# archive.py

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aswwu.archive_models import ArchiveBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
archive_engine = create_engine("sqlite:///../../databases/archives.db")

# same for archives
ArchiveBase.metadata.bind = archive_engine
archive_dbs = sessionmaker(bind=archive_engine)
archive_db = archive_dbs()

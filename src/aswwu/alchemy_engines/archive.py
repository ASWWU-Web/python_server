# archive.py

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.aswwu.archive_models import ArchiveBase
from settings import config

logger = logging.getLogger(config.logging.get('log_name'))

# defines the databases URLs relative to "server.py"
archive_engine = create_engine("sqlite:///" + config.database.get('databases') + "/archives.db")

# same for archives
ArchiveBase.metadata.bind = archive_engine
archive_dbs = sessionmaker(bind=archive_engine)
archive_db = archive_dbs()

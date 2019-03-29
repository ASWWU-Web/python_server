from os import getenv
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(getenv('RDS_USERNAME'),
                                                               getenv('RDS_PASSWORD'),
                                                               getenv('RDS_HOSTNAME', '127.0.0.1'),
                                                               getenv('RDS_PORT', '3306'),
                                                               getenv('RDS_DB_NAME')))
connection = engine.connect()

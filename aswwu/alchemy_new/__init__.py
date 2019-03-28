from os import getenv
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(getenv('DB_USER'),
                                                               getenv('DB_PASSWORD'),
                                                               getenv('DB_IP', '127.0.0.1'),
                                                               getenv('DB_PORT', '3306'),
                                                               getenv('DB_NAME')))
connection = engine.connect()

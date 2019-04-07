from os import getenv
from sqlalchemy import create_engine

database_url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(getenv('RDS_USERNAME'),
                                                                       getenv('RDS_PASSWORD'),
                                                                       getenv('RDS_HOSTNAME', '127.0.0.1'),
                                                                       getenv('RDS_PORT', '3306'),
                                                                       getenv('RDS_DB_NAME'))
engine = create_engine(database_url, convert_unicode=True)
connection = engine.connect()

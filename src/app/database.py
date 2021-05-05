from sqlalchemy import create_engine
from sqlalchemy.orgm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import config

engine = create_engine(config.SQLITE_DB, convert_unicode = True)
db_session = scoped_session(sessionmaker(autocommit = False, autoflush = False, bind = engine))

Base = declarative_base()
Base.query = db_session.query_property()
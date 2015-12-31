from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
from sqlalchemy.orm.exc import NoResultFound
from zope.sqlalchemy import ZopeTransactionExtension

import datetime
import pyramid
import pyramid.threadlocal

import logging
log = logging.getLogger(__name__)

# db = scoped_session(sessionmaker())
db = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class HTTPUrl(Base):
	__tablename__ = 'http'
	id = Column(Integer, primary_key=True, index=True)
	created = Column(DateTime, nullable=False)
	host_url = Column(Text, nullable=False)


class Checked(Base):
	__tablename__ = 'checks'
	id = Column(Integer, primary_key=True, index=True)
	http_url_id = Column(Integer, ForeignKey("http.id"), nullable=False, index=True)
	checked_on = Column(DateTime, nullable=False)
	was_it_up = Column(Boolean)

import unittest
import datetime
import transaction
from bs4 import BeautifulSoup
# from mongoengine import connect
# from pyramid import testing
from pyramid.paster import get_app
from models import *

import logging
log = logging.getLogger(__name__)


class BasicUserTest(unittest.TestCase):
	def setUp(self):
		app = get_app('development.ini')
		self.engine = create_engine('sqlite://')

		# db = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
		db = scoped_session(sessionmaker())
		db.configure(bind=self.engine)
		Base.metadata.bind = self.engine
		Base.metadata.create_all(self.engine)

		from webtest import TestApp
		self.testapp = TestApp(app)

	def tearDown(self):
		del self.testapp
		Base.metadata.drop_all(self.engine)

	def test_urls(self):
		self.testapp.get('/')
		self.testapp.get('/api/xmlrpc')

	def test_google_up(self):
		res = self.testapp.get('/')
		res.form['url'] = 'http://google.com'
		nres = res.form.submit()
		# log.debug(nres.text)
		soup = BeautifulSoup(nres.text)
		url = soup.find('h1', id='up')
		log.debug(url)
		assert url
		r = db.query(HTTPUrl).filter(HTTPUrl.host_url == 'http://google.com').one()
		c = db.query(Checked).filter(Checked.http_url_id == r.id).one()
		assert c


	@unittest.skip("not finished")
	def test_head(self):
		res = self.testapp.get('/')
		res.form['url'] = 'http://google.com'
		nres = res.form.submit()
		nres = nres.follow()
		# log.debug(nres.text)
		soup = BeautifulSoup(nres.text)
		url = soup.find('h1', id='url')
		assert url.text
		#test HEAD request
		res = self.testapp.head(url.text)
		assert res.status_int == 200

	@unittest.skip("not finished")
	def test_duplicate(self):
		res = self.testapp.get('/')
		res.form['url'] = 'http://google.co.uk'
		nres = res.form.submit()
		nres = nres.follow()
		# log.debug(nres.text)
		soup = BeautifulSoup(nres.text)
		url = soup.find('h1', id='url')
		res = self.testapp.get('/')
		res.form['url'] = 'http://google.co.uk'
		nres = res.form.submit()
		nres = nres.follow()
		# log.debug(nres.text)
		soup = BeautifulSoup(nres.text)
		url2 = soup.find('h1', id='url')
		log.info(url.text)
		assert url2.text == url.text


from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import *
from mongoengine import connect
import datetime
import transaction
import bleach
import requests
import requests.exceptions

from models import *
from validate_url import *

import logging

log = logging.getLogger(__name__)


class HostDown(Exception):
	pass


@view_defaults(http_cache=(None, {'private': True}), route_name='index', renderer='templates/bs-index.jinja2')
class IndexView(object):
	def __init__(self, request):
		self.request = request
		self.title = 'HostDown? | What is the status of your servers? | hostdown.co'

	@view_config(request_method='HEAD')
	def head(self):
		return Response(status_code=200, headers={'X-Powered-By': 'hostdown.co'})

	@view_config(request_method='GET')
	def get(self):
		return {'title': self.title, 'description': 'Free website monitoring tool.'}

	@view_config(request_method='POST')
	def post(self):
		try:
			try:
				if self.request.POST['csrf_token'] != self.request.session.get_csrf_token():
					return self.get()
			except KeyError:
				raise HTTPBadRequest
			finally:
				self.request.session.new_csrf_token()

			# this needs to be set as its used in the exception handling
			user_url = bleach.clean(self.request.POST['url'].strip())

			if not user_url:
				return self.get()

			# Do the hard work of validating the user url
			clean_url, hostname, ip = validate_url(user_url)

			# Do we already have this in the database or looked at it recently?
			# with transaction.manager:
			try:
				host = db.query(HTTPUrl).filter(HTTPUrl.host_url == hostname).one()

				try:
					# Already been checked with in the last minute
					last = db.query(Checked).filter(Checked.http_url_id == host.id).filter(
						Checked.checked_on >= (datetime.datetime.now() - datetime.timedelta(minutes=1))).one()
					return {'title': self.title, 'input': user_url, 'result': host, 'last': last, 'isup': True}
				except NoResultFound:
					pass
			except NoResultFound:
				host = HTTPUrl(host_url=hostname, created=datetime.datetime.now())
				db.add(host)
				db.flush()

			try:
				user_agents = [
					'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
					'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
					'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
					'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
				]

				# Do a HEAD check on the URL
				import random

				headers = {'User-Agent': random.choice(user_agents), 'Referer': 'http://hostdown.co'}
				r = requests.head(hostname, headers=headers, timeout=5, allow_redirects=True)
				log.debug(r.status_code)
				if r.status_code == requests.codes.ok:
					log.info(r.history)
					log.info(r.url)
					pass
				else:
					raise HostDown('Invalid URL or bad response ({} {})'.format(r.status_code, r.reason))
			except requests.exceptions.Timeout:
				raise HostDown('Invalid URL (timeout on request)')
			except requests.exceptions.ConnectionError:
				raise HostDown('Invalid URL (connection error on request)')

			# need to update the real host as it might have redirected from the submitted one
			r_clean_url, r_hostname, r_ip = validate_url(r.url)

			if hostname != r_hostname:
				host.redirected_to = r_hostname

			db.add(Checked(http_url_id=host.id, checked_on=datetime.datetime.now(), was_it_up=True))
			db.flush()
			return {'title': self.title, 'input': user_url, 'result': host, 'isup': True}

		except HostDown:
			db.add(Checked(http_url_id=host.id, checked_on=datetime.datetime.now(), was_it_up=False))
			db.flush()
			return {'title': self.title, 'input': user_url, 'result': host, 'isup': False}

		except URLInvalid as e:
			return {'title': self.title, 'input': user_url, 'error': e.message}


@view_defaults(http_cache=(3600, {'public': True}), route_name='terms', renderer='templates/terms.jinja2')
class TermsView(object):
	def __init__(self, request):
		self.request = request

	@view_config(request_method='GET')
	def get(self):
		return {'title': 'Terms and Conditions', 'description': 'Terms and Conditions'}

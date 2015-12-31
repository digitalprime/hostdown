import socket
import requests
import requests.exceptions
from urlparse import urlparse
import logging
log = logging.getLogger(__name__)


class URLInvalid(Exception):
	pass


def validate_url(url_string):
	try:
		url = urlparse(url_string, allow_fragments=False)
		log.debug(url)

		if url.scheme is '':
			url_string = '%s%s' % ('http://', url_string)
			url = urlparse(url_string, allow_fragments=False)

		if url.scheme not in ['http', 'https']:
			raise URLInvalid('Not a supported URL schema')

		if url.netloc is '' and url.path is '':
			raise URLInvalid('Invalid URL')

		if url.username is not None or url.password is not None:
			raise URLInvalid('Your not allowed to have username or password parts')

		if url.port is not None:
			raise URLInvalid('Your not allowed an explicit port number')

		# Does the URL resolve
		try:
			ip = socket.gethostbyname(url.hostname)
			log.debug(ip)
		except socket.gaierror:
			log.debug(url.hostname)
			raise URLInvalid('URL does not resolve or does not exist')
		except TypeError:
			log.debug(url.hostname)
			raise URLInvalid('Invalid URL (lookup).')

		return url.geturl(), url.scheme + '://' +url.hostname, ip
	except:
		raise


def trace_url(url):
	try:
		log.debug('trace start')
		user_agents = [
			'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
			'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
			'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
		]

		# Do a HEAD check on the URL
		import random
		headers = {'User-Agent': random.choice(user_agents), 'Referer': 'http://g0t.co'}
		r = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
		log.debug(r.status_code)
		log.debug(r.url)
		log.debug(r.history)
		log.debug('trace end')
		return r.url
	except requests.exceptions.Timeout as e:
		log.info(e.message)
	except requests.exceptions.ConnectionError:
		log.info(e.message)

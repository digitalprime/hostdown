from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import *
from pyramid.renderers import render_to_response
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

import logging
log = logging.getLogger(__name__)


@view_defaults(http_cache=(None, {'private': True}), route_name='rpc')
class Pingback(object):
	def __init__(self, request):
		self.request = request

	@view_config(request_method=('GET', 'HEAD'))
	def invalid(self):
		# Broken web crawlers seem to end up here. 200 it and move on
		return Response(status_code=200, headers={'X-Powered-By': 'hostdown.co'})

	@view_config(request_method='POST')
	def post(self):
		try:
			mailer = get_mailer(self.request)
			message = Message(subject="RPC", sender="noreply@hostdown.co", recipients=["darrenc@localhost"], body=self.request.body)
			mailer.send(message)

			r = render_to_response('templates/xmlrpc_response.jinja2', {'value': 'ok'}, request=self.request)
			r.content_type = 'text/xml'
			r.status_int = 200
			return r
		except:
			raise


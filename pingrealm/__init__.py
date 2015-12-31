from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS
from pyramid.view import notfound_view_config
from pyramid.view import forbidden_view_config
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from models import *


class RootFactory(object):
	__acl__ = [
		(Allow, Everyone, 'view'),
		(Allow, Authenticated, 'moderate'),
		(Allow, 'g:editor', 'edit'),
		(Allow, 'g:admin', ALL_PERMISSIONS)
	]

	def __init__(self, request):
		self.request = request


@notfound_view_config()
def notfound(request):
	response = render_to_response('templates/notfound.jinja2',
								  {'title': 'Nope, can not find that one!',
								   'nocanonical': True,
								   'description': 'The thing your looking for is gone!',
								   'keywords': 'not found'}, request=request)
	response.status_int = 404
	return response


@forbidden_view_config()
def forbidden(request):
	return HTTPFound(request.route_url("index"))


def main(global_config, **settings):
	engine = engine_from_config(settings, 'sqlalchemy.')
	db.configure(bind=engine)
	Base.metadata.bind = engine

	authn_policy = AuthTktAuthenticationPolicy('D24AD44D67115C79B2848FE932556', cookie_name='hd', domain='hostdown.co')
	authz_policy = ACLAuthorizationPolicy()
	my_session_factory = SignedCookieSessionFactory('2B156E211E49488AB4CD5B28BB763')
	config = Configurator(settings=settings, session_factory=my_session_factory, root_factory=RootFactory)
	config.set_authentication_policy(authn_policy)
	config.set_authorization_policy(authz_policy)

	config.include('pyramid_jinja2')
	config.add_jinja2_search_path("pingrealm:templates")

	config.add_static_view('static', 'static', cache_max_age=3600)
	config.add_route('index', '/')
	config.add_route('terms', '/i/terms')
	config.add_route('contact', '/i/contact')

	config.add_route('rpc', '/api/xmlrpc')

	# assert config.registry.settings['mongodb.database']
	# connect(config.registry.settings['mongodb.database'])

	config.scan()
	config.commit()

	config.get_jinja2_environment().filters['timeago'] = filters.time_ago_in_words
	config.get_jinja2_environment().filters['format_number'] = filters.format_number
	config.get_jinja2_environment().filters['markdown_file'] = filters.markdown_file
	config.get_jinja2_environment().filters['urlshort'] = filters.urlshort

	config.get_jinja2_environment().trim_blocks = True
	config.get_jinja2_environment().lstrip_blocks = True
	return config.make_wsgi_app()

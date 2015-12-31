from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from wtforms import *
from wtforms.validators import Required, Optional, URL

from models import *
import bleach


class ContactForm(Form):
	name = TextField('Name', validators=[validators.Length(min=1, max=120), Required()])
	email = TextField('Email Address', validators=[validators.Email(), Required()])
	subject = TextField('Subject', validators=[validators.Length(min=1, max=120), Required()])
	body = TextAreaField('Body', validators=[validators.Length(min=1, max=1024), Required()])


@view_defaults(http_cache=(3600, {'public': True}), route_name='contact', renderer='templates/contact.jinja2')
class ContactView(object):
	def __init__(self, request):
		self.request = request

	@view_config(request_method='GET')
	def get(self):
		try:
			form = ContactForm()
			return {'title': 'Contact g0t', 'description': 'Blah blah', 'form': form}
		except:
			raise

	@view_config(request_method='POST')
	def post(self):
		try:
			form = ContactForm(self.request.POST)
			if form.validate():
				subject = bleach.clean(form.subject.data)
				address = bleach.clean(form.email.data)
				body = u'{}\n\n{}'.format(bleach.clean(form.body.data), bleach.clean(form.name.data))
				mailer = get_mailer(self.request)
				message = Message(subject=subject, sender=address, recipients=["darrenc@localhost"],
								  body=body)
				mailer.send(message)

				return HTTPFound(self.request.route_url("index"))

			return {'title': 'Contact g0t', 'description': 'Blah blah', 'form': form}
		except:
			raise
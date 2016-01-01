import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
	'pyramid',
	'pyramid_debugtoolbar',
	'pyramid_tm',
	'SQLAlchemy',
	'psycopg2',
	'zope.sqlalchemy',
	'transaction',
	'waitress',
	'webhelpers',
	'wtforms',
	'pyramid_jinja2',
	'pyramid-mailer',
	'pyramid_exclog',
	'bleach',
	'natural',
	'colander',
	'requests',
	'markdown',
	'beautifulsoup4'
]

setup(name='pingrealm',
	  version='0.2',
	  description='pingrealm',
	  long_description='',
	  classifiers=[
		  "Programming Language :: Python",
		  "Topic :: Internet :: WWW/HTTP",
		  "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
	  ],
	  author='Darren Cree',
	  author_email='darren.cree@gmail.com',
	  url='',
	  keywords='web wsgi',
	  packages=find_packages(),
	  include_package_data=True,
	  zip_safe=False,
	  test_suite='pingrealm',
	  install_requires=requires,
	  entry_points="""\
      [paste.app_factory]
      main = pingrealm:main
      [console_scripts]
      initialize_pingrealm = pingrealm.scripts.initializedb:main
      """,
)

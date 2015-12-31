from pyramid.paster import get_app, setup_logging
import os

os.environ['PYTHON_EGG_CACHE'] = '/tmp/python-eggs'
ini_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'production.ini')
setup_logging(ini_path)
application = get_app(ini_path, 'main')

import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../data.sqlite')
#URL_MAIN_WEBSERVICE = 'http://127.0.0.1:5000/'
##config.py
FLASK_PIKA_PARAMS = {
    'host':'localhost',      #amqp.server.com
}

# optional pooling params
FLASK_PIKA_POOL_PARAMS = {
    'pool_size': 8,
    'pool_recycle': 600
}
DEBUG = False
SECRET_KEY = 'top-secret!'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                          'sqlite:///' + db_path



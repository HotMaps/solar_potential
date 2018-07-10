import os
from flask import Flask, jsonify, g
from .constant import SIGNATURE,CM_NAME,URL_MAIN_WEBSERVICE
from .decorators import json, no_cache, rate_limit
from flasgger import Swagger



def create_app(config_name):
    """Create an application instance."""
    app = Flask(__name__)
    """Create swagger documentation"""
    swagger = Swagger(app)
    # apply configuration
    cfg = os.path.join(os.getcwd(), 'config', config_name + '.py')
    app.config.from_pyfile(cfg)

    # initialize extensions


    # register blueprints
    from .api_v1 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/computation-module')

    # register an after request handler
    @app.after_request
    def after_request(rv):
        headers = getattr(g, 'headers', {})
        rv.headers.extend(headers)
        return rv


    return app

import json

import werkzeug.exceptions
from flask import Flask
from sqlalchemy.exc import OperationalError


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object('github_oauth_gateway.conf.Config')

    if testing:
        app.config.from_object('github_oauth_gateway.conf.TestConfig')

    from github_oauth_gateway.db import db
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('db.create_all: created tables')
        except OperationalError:
            app.logger.info('db.create_all: did NOT create tables, maybe they already exist?')

    # add generic status page
    @app.route('/status')
    def status():
        return 'OK'

    # register generic json error handler
    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors.

        Source: https://flask.palletsprojects.com/en/1.1.x/errorhandling/#generic-exception-handlers
        """
        response = e.get_response()
        response.data = json.dumps({
            'code': e.code,
            'name': e.name,
            'message': e.description,
        })
        response.content_type = 'application/json'
        return response

    # register API
    from github_oauth_gateway.api import blueprint
    app.register_blueprint(blueprint, url_prefix='/api/v1')

    return app

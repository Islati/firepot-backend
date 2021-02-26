"""
This modules purpose is to create instances of the application, configure them, and return
them for serving via WSGI.
"""

import os
from flask import Flask

from firepot.config import Config, TestConfig
from firepot.extensions import db, cors, hashing, migrate
import logging
import logging.handlers

import glob
import json
from logging.handlers import RotatingFileHandler

from firepot.models import Item

LOGGER = logging.getLogger(__name__)


def configure_logging(app):
    def configure_logging(app):
        """
        Configure logging for application, and flask.
        :param app: pantheon application instance
        """

        module_loggers = [
            app.logger,
            logging.getLogger('werkzeug'),
            logging.getLogger('firepot'),
        ]

        formatter = '%(asctime)s: %(levelname)-8s: %(module)s:%(funcName)s:%(lineno)d :: %(message)s'

        formatting = logging.Formatter(formatter)

        log_file = os.path.join(app.config['LOG_FOLDER'], 'app.log')

        if not os.path.exists(log_file):
            print("Log file does not exist")

            if not os.path.exists(app.config['LOG_FOLDER']):
                print("Nor does the log folder")

                try:
                    os.mkdir(app.config['LOG_FOLDER'])
                except:
                    print("Failed to create log folder")

        file_handler = RotatingFileHandler(
            'app.log',
            maxBytes=100000,
            backupCount=1
        )

        file_handler.setLevel("DEBUG")
        file_handler.setFormatter(formatting)

        console_handler = logging.StreamHandler()
        console_handler.setLevel('DEBUG')
        console_handler.setFormatter(formatting)

        for module_logger in module_loggers:
            module_logger.setLevel(logging.DEBUG)
            module_logger.addHandler(file_handler)
            if not app.config['TESTING']:
                module_logger.addHandler(console_handler)


def register_blueprints(app):
    from firepot.routes import auth_blueprint, store_blueprint, admin_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(store_blueprint)
    app.register_blueprint(admin_blueprint)


def configure_extensions(app):
    """
    Configure all extensions for the application
    :param app: app to configure
    """

    db.init_app(app)

    try:
        LOGGER.debug("Attempting to create database tables")
        db.create_all(app=app)
        LOGGER.debug("Created database tabled")

    except Exception as e:
        LOGGER.debug("Exception with db.create_all() - Duplicates??")

    #     todo check if tables exist

    hashing.init_app(app=app)
    cors.init_app(app=app)
    migrate.init_app(app=app)


def create_app(config_override=None, testing=False):
    """
    Method called when creating an application to serve.
    :param config_override: settings to override in application
    :param testing: whether or not it's being ran in a test environment/
    :return: instance configured and ready
    """

    app = Flask(__name__)

    if testing is True:
        config = TestConfig()
    else:
        config = config_override if config_override is not None else Config()

    app.config.from_object(config)

    configure_logging(app)

    LOGGER.debug("Application logging has been configured")

    register_blueprints(app)

    LOGGER.debug("Blueprints have been registered")

    configure_extensions(app)

    LOGGER.debug("Registered extensions")

    if not is_setup_finalized(app=app):
        with app.app_context():
            # Create Permissions.
            from firepot.models import Permission, User, SetupRecord
            from firepot import permissions

            admin_permission = Permission.get_or_create(node="firepot.admin")
            admin_permission.save(commit=True)

            import datetime
            admin_user = User(first_name="Brandon", last_name="Curtis", email="admin@firepot.ca",
                              phone_number="7095369785", password="testing1",
                              birth_date=datetime.datetime.fromisoformat("1995-01-13"))
            admin_user.save(commit=True)
            admin_user.add_permission(permissions.ADMIN_PERMS)
            admin_user.save(commit=True)

            setup_record = SetupRecord(status="setup")
            setup_record.save(commit=True)

    # @app.after_request
    # def after_request(response):
    #     response.headers.add('Access-Control-Allow-Origin', '*')
    #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    #     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    #     LOGGER.info("Updated response headers with after request")
    #     return response

    return app


def is_setup_finalized(app):
    from firepot.models import SetupRecord

    with app.app_context():
        record = SetupRecord.get_by_id(1)

        if record is None:
            return False

        return record.status != "incomplete"

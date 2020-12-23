import os


class Config(object):
    SECRET_KEY = 'ap!g0f4a5td4ddy'

    BASE_FOLDER = os.path.expanduser('~/PycharmProjects/firepot/')

    LOG_FOLDER = os.path.expanduser(os.path.join(BASE_FOLDER, "data/logs/"))

    SQLALCHEMY_DATABASE_URI = "postgresql://brandon:testing@localhost/brandon"

    DEBUG_ADMIN_AUTHORIZATION_BEARER = "jb0pcwCutK"
    DEBUG_USER_AUTHORIZATION_BEARER = "ZxHtrwpS7K"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG_TB_ENABLED = False
    DEBUG = False
    TESTING = False

    LOGLEVEL = "DEBUG"

    HASHING_METHOD = "sha512"
    HASHING_ROUNDS = 1

    ENV = 'development'


class TestConfig(Config):
    """
    Configuration object from :class:`mobile.config.BaseConfig`
    Configuration for Flask. Applies to all applications using
    :method:`mobile.factory.configure_app()`
    """
    SECRET_KEY = 'ap!g0f4a5td4ddy'

    LOGLEVEL = "DEBUG"

    ENV = 'testing'

    DEBUG = True
    TESTING = True

    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://brandon:testing@localhost/testing"

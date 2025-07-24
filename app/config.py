from decouple import config
from datetime import timedelta

class Config(object):

    DOMAIN = config('DOMAIN', cast=str)
    SECRET_KEY = config('SECRET_KEY', cast=str)
    DEBUG = config('DEBUG', cast=bool)
    PROD_TARGET = config('PROD_TARGET', cast=str)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENCRYPTION_KEY = config('ENCRYPTION_KEY', cast=str)

    TRAP_HTTP_EXCEPTIONS = True

class ProductionConfig(Config):

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(seconds=28800)
    PROPAGATE_EXCEPTIONS = False

    if Config.PROD_TARGET == 'gae':
        # Google App Engine F4 (2.4GB RAM, 4 vCPUs)
        # GAE has connection limits and auto-scaling considerations
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,  # Conservative for GAE connection limits
            'max_overflow': 5,  # Total 10 connections max per instance
            'pool_timeout': 30,  # Fail fast in serverless environment
            'pool_recycle': 3600,  # 1 hour (GAE handles most connection issues)
            'pool_pre_ping': True  # Important for GAE's connection management
        }

        SQLALCHEMY_DATABASE_URI = '{}://{}:{}@/{}?unix_socket=/cloudsql/{}'.format(
            config('DB_ENGINE'),
            config('DB_USERNAME'),
            config('DB_PASS'),
            config('DB_NAME'),
            config('DB_HOST')
        )

    elif Config.PROD_TARGET == 'ubuntu_server':
        # Ubuntu Server (32GB RAM) - Can handle more connections
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 20,  # More connections for dedicated server
            'max_overflow': 10,  # Total 30 connections max
            'pool_timeout': 60,  # Can wait longer on dedicated server
            'pool_recycle': 3600,  # 1 hour
            'pool_pre_ping': True  # Check connection health
        }

        SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
            config('DB_ENGINE'),
            config('DB_USERNAME'),
            config('DB_PASS'),
            config('DB_HOST'),
            config('DB_PORT', default=3306),
            config('DB_NAME')
        )

    else:
        # Local or Raspberry Pi 3+ (1GB RAM) - Very limited resources
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 2,  # Minimal connections
            'max_overflow': 1,  # Total 3 connections max
            'pool_timeout': 20,  # Fail fast to prevent memory issues
            'pool_recycle': 1800,  # 30 min (more frequent recycling)
            'pool_pre_ping': True,  # Essential for Pi's limited resources
            'echo_pool': False  # Disable pool logging to save resources
        }

        SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
            config('DB_ENGINE'),
            config('DB_USERNAME'),
            config('DB_PASS'),
            config('DB_HOST'),
            config('DB_PORT', default=3306),
            config('DB_NAME')
        )



class DebugConfig(Config):

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(seconds=28800)
    PROPAGATE_EXCEPTIONS = True

    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE'),
        config('DB_USERNAME'),
        config('DB_PASS'),
        config('DB_HOST'),
        config('DB_PORT', default=3306),
        config('DB_NAME')
    )

# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}

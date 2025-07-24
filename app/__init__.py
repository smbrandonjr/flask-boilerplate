import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta
from importlib import import_module
from flask import Flask, request, url_for, render_template, session, flash, redirect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from app.config import Config


db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
csrf = CSRFProtect()
migrate = Migrate()


def setup_logging(app):
    if not Config.DEBUG:
        app.logger.setLevel(logging.INFO)
    else:
        try:
            handler = RotatingFileHandler("app.log", maxBytes=100000)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)
            app.logger.setLevel(logging.DEBUG)
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            app.logger.addHandler(console_handler)
            app.logger.setLevel(logging.DEBUG)


def log_exception(logger, context, exception, level='error'):
    log_message = f"{context}: {str(exception)}"
    if level == 'debug':
        logger.debug(log_message)
    elif level == 'warning':
        logger.warning(log_message)
    else:
        logger.error(log_message)


def redirect_url(default='global.index'):
    return request.args.get('next') or request.referrer or url_for(default)


def register_extensions(app):
    db.init_app(app)
    oauth.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    for module_name in ['user']:
        module = import_module(f'app.routes.{module_name}')
        app.register_blueprint(module.blueprint)


def configure_database(app):
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            log_exception(app.logger, "Configuring Database", e)

    @app.teardown_request
    def shutdown_session(exception=None):
        if exception:
            log_exception(app.logger, "Database Session Shutdown", exception, level='debug')
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    setup_logging(app)

    # Register custom datetimeformat filter for Jinja
    def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
        import datetime
        try:
            if isinstance(value, (int, float)):
                # Assume unix timestamp (seconds)
                dt = datetime.datetime.utcfromtimestamp(value)
            elif isinstance(value, datetime.datetime):
                dt = value
            else:
                return value
            return dt.strftime(format)
        except Exception:
            return value

    app.jinja_env.filters['datetimeformat'] = datetimeformat

    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(seconds=28800)


    @app.errorhandler(Exception)
    def handle_error(e):
        try:
            # Get detailed traceback info
            import traceback, json
            tb = traceback.format_exc()

            request_info = {
                'url': request.url,
                'method': request.method,
                'endpoint': request.endpoint,
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'args': dict(request.args)
            }

            # Structure the error for GCP logging
            error_dict = {
                'severity': 'ERROR',
                'exception_type': type(e).__name__,
                'message': str(e),
                'request': request_info,
                'traceback': tb
            }

            # Log as JSON for GCP structured logging
            app.logger.error(json.dumps(error_dict))

            status_code = getattr(e, 'code', 500)
            error_messages = {
                400: "Bad Request - The server cannot process your request.",
                401: "Authentication Required - Please log in to continue.",
                403: "Access Denied - You don't have permission to access this resource.",
                404: "Page Not Found - The requested resource doesn't exist or has been moved.",
                429: "Too Many Requests - Please wait a moment before trying again.",
                500: "Internal Server Error - Something went wrong on our end.",
                502: "Bad Gateway - We're having trouble connecting to our services.",
                503: "Service Unavailable - We're temporarily unavailable. Please try again later.",
                504: "Gateway Timeout - The server took too long to respond."
            }
            error_message = error_messages.get(status_code, "An unexpected error has occurred.")
            error_details = str(e) if str(e) and str(e) != error_message else None
            if status_code == 401:
                flash('Authentication Required - Please log in to continue.', 'error')
                return redirect(url_for('user.login'))
            return render_template('error/error.html', error_code=status_code, error_title=f"Error {status_code}",
                                   error_message=error_message, error_details=error_details), status_code
        except Exception as er:
            app.logger.error(f'main.py handle_error() exception: {str(er)}')
            return render_template('error/error.html', error_code=500, error_title="Internal Server Error",
                                   error_message="Something unexpected went wrong.", error_details=None), 500

    return app
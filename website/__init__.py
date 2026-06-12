from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from os.path import join, dirname, realpath


db = SQLAlchemy()
DB_name = "database.db"


def load_dotenv():
    import os
    env_path = join(dirname(dirname(realpath(__file__))), '.env')
    if path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip())


load_dotenv()


def get_database_uri():
    import os
    # Set DATABASE_URL (e.g. postgresql://user:pass@host:5432/dbname) to use
    # RDS/Postgres; falls back to local SQLite when unset.
    url = os.environ.get('DATABASE_URL')
    if url:
        # SQLAlchemy requires the postgresql:// scheme; some providers hand
        # out the legacy postgres:// form
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    return f'sqlite:///{DB_name}'


# creates app for flask
def create_app():
    import os
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY', 'uoihweiuhb ewfuewhfwefhewfuih')
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .oauth import oauth_bp, init_oauth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(oauth_bp, url_prefix='/')
    init_oauth(app)
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), './static/uploads/')

    # if not os.path.isdir(UPLOAD_FOLDER):
    #     os.makedirs(UPLOAD_FOLDER)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    
    # app.config['UPLOAD_FOLDER'] = os.path.join(
    #     os.path.dirname(__file__), 'static/uploads')

    from .models import User, Favorite

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == user_id).first()

    return app

def create_database(app):
    # Multiple gunicorn workers boot concurrently and all run create_all;
    # losers of the race see "table already exists" — harmless, ignore it
    from sqlalchemy.exc import OperationalError, ProgrammingError
    with app.app_context():
        try:
            db.create_all()
            print('Created the database!')
        except (OperationalError, ProgrammingError) as e:
            if 'already exists' not in str(e):
                raise
#made another change 
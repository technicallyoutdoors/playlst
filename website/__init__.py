from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from os.path import join, dirname, realpath


db = SQLAlchemy()
DB_name = "database.db"


# creates app for flask
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'uoihweiuhb ewfuewhfwefhewfuih'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_name}'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
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
    if not path.exists('website/' + DB_name):
        with app.app_context():
            db.create_all()
            print('Created the database!')
#made another change 
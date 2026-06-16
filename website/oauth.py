import os
import secrets

from flask import Blueprint, flash, redirect, url_for
from flask_login import login_user
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash

from .models import User
from . import db

oauth = OAuth()
oauth_bp = Blueprint('oauth_bp', __name__)

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')


def init_oauth(app):
    oauth.init_app(app)

    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        oauth.register(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )


def _login_or_create_user(email, first_name, last_name):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            first_name=first_name or email.split('@')[0],
            last_name=last_name or '',
            # OAuth users never use this password; random so it can't be guessed
            password=generate_password_hash(secrets.token_urlsafe(32), method='pbkdf2:sha256'),
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created!', category='success')
    login_user(user, remember=True)
    return redirect(url_for('auth.home'))


@oauth_bp.route('/login/google')
def google_login():
    client = oauth.create_client('google')
    if client is None:
        flash('Google sign-in is not configured yet.', category='error')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('oauth_bp.google_callback', _external=True)
    return client.authorize_redirect(redirect_uri)


@oauth_bp.route('/callback/google')
def google_callback():
    client = oauth.create_client('google')
    if client is None:
        return redirect(url_for('auth.login'))
    try:
        token = client.authorize_access_token()
        info = token.get('userinfo')
        if not info or not info.get('email'):
            raise ValueError('No email returned from Google')
    except Exception:
        flash('Google sign-in failed. Please try again.', category='error')
        return redirect(url_for('auth.login'))
    return _login_or_create_user(
        info['email'], info.get('given_name'), info.get('family_name'))

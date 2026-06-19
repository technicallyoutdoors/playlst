from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Favorite
from . import db
import sqlite3
import json


views = Blueprint('views', __name__)


@views.route('/')
def main():
    return render_template("main.html", user=current_user)


@views.route('/privacy')
def privacy():
    return render_template("privacy.html", user=current_user)


@views.route('/terms')
def terms():
    return render_template("terms.html", user=current_user)

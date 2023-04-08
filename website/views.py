from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Favorite
from . import db
import sqlite3
import json


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


# @views.route('/delete_favorite', methods=['POST'])
# def delete_favorite():
#     favorite = json.loads(request.data)
#     favoriteTitle = data['favoriteTitle']
#     favorite = favorite.query.get(favoriteTitle)
#     if favorite:
#         if favorite.user_id == current_user.id:
#             db.session.delete(favorite)
#             db.session.commit()
#             return jsonify({})

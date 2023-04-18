from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    photo = db.relationship('Photo', uselist=False)
    password = db.Column(db.String(60), nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    favorites = db.relationship('Favorite', lazy='dynamic')

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', overlaps="favorites")


class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    code = db.Column(db.String(6), unique=True)
    members = db.relationship('User', backref='family', lazy=True)
    # favorites = db.relationship('Favorite', secondary='user', lazy='subquery',
    #                              backref=db.backref('families', lazy=True))

    
class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

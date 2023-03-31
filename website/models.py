from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(60), nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    favorites = db.relationship('Favorite')

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')


# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True)
#     password = db.Column(db.String(150))
#     first_name = db.Column(db.String(150))
#     favorites = db.relationship('Favorite')
#     family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
#     code = db.Column(db.String(6), unique=True, nullable=True)
    
# class Favorite(db.Model):
#     id = db.Column(db.String(50), primary_key=True)
#     title = db.Column(db.String(150))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     image = db.Column(db.String(200))   


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

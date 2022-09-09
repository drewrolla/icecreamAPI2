from secrets import token_hex
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

user_icecream = db.Table('user_icecream',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('icecream_id', db.Integer, db.ForeignKey('icecream.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(300), nullable=False)
    apitoken = db.Column(db.String, default=None, nullable=True)
    shop = db.relationship("Icecream",
        secondary = user_icecream,
        backref = 'foodie',
        lazy = 'dynamic'
    )

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.apitoken = token_hex(16)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'token': self.apitoken
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def getShops(self):
        list_of_tuples = db.session.query(user_icecream).filter(user_icecream.u.user_id==self.id).all()
        return [Icecream.query.get(t[1]) for t in list_of_tuples]

    def saveToDB(self):
        db.session.commit()

    def saveShops(self, icecream):
        self.user_icecream.append(icecream)
        db.session.commit()

    def removeShops(self, icecream):
        self.user_icecream.remove(icecream)
        db.session.commit()

class Icecream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    rating = db.Column(db.Integer)
    address = db.Column(db.String)
    img_url = db.Column(db.String)
    website = db.Column(db.String)

    def __init__(self, name, rating, address, img_url, website):
        self.name = name
        self.rating = rating
        self.address = address
        self.img_url = img_url
        self.website = website

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'address': self.address,
            'img_url': self.img_url,
            'website': self.website
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
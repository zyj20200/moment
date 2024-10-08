from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Moment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, default="张三")
    avatar = db.Column(db.String(255), nullable=False, default="a.jpg")
    content = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='moment', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
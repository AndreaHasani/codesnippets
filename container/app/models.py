from flask import current_app
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
from datetime import date
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class Answers(db.Model):
    __tablename__ = 'answers'

    id = db.Column('id', db.Integer(), primary_key=True, nullable=False)
    votes = db.Column('votes', db.Integer(), nullable=False)
    answer = db.Column('answer', db.TEXT(), nullable=False)
    accepted = db.Column('accepted', db.Boolean(), nullable=False, default=0)
    source = db.Column('source', db.String(128), nullable=False)
    author = db.Column('author', db.String(128), nullable=False)
    url = db.Column('url', db.String(256), nullable=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)


class Questions(db.Model):
    __tablename__ = 'questions'

    id = db.Column('id', db.Integer(), primary_key=True, nullable=False)
    title = db.Column('title', db.String(128), nullable=False)
    tags = db.Column('tags', db.String(128), nullable=False)
    votes = db.Column('votes', db.Integer(), nullable=False)
    answers_num = db.Column('answers_num', db.Integer(), nullable=False)
    answered = db.Column('answered', db.Boolean(), nullable=False, default=0)
    source = db.Column('source', db.String(128), nullable=False)
    url = db.Column('url', db.String(256), nullable=True)
    answers = db.relationship('Answers', backref='question')


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column('id', db.Integer(), primary_key=True, nullable=False)
    name = db.Column('name', db.String(128), nullable=False)
    password = db.Column('password', db.String(128), nullable=False)
    admin = db.Column('admin', db.Boolean(), nullable=False, default=False)

    def __init__(self, id):
        self.id = id


    @property
    def is_admin(self):
        if self.admin:
            return True
        else:
            return False

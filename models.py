from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False) 
    avatar = db.Column(db.String(300), default='uploads/avatars/default.png')
    created = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='author', lazy=True)
    answers = db.relationship('Answer', back_populates='user', lazy=True)
    votes = db.relationship('Vote', backref='voter', lazy=True)
    comments = db.relationship('Comment', backref='commenter', lazy=True)
    questions = db.relationship('Question', back_populates='user')


    def __repr__(self):
        return f"<User {self.username}>"

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255))  
    image = db.Column(db.String(255), nullable=True)
    vote = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    best_answer = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('Answer',back_populates='question',lazy=True,foreign_keys='Answer.question_id')
    comments = db.relationship('Comment', backref='question', lazy=True)
    votes = db.relationship('Vote', backref='question', lazy=True)
    user = db.relationship('User', back_populates='questions')



    def __repr__(self):
        return f"<Question {self.title}>"



class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.Text, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    question = db.relationship('Question', back_populates='answers', foreign_keys=[question_id])
    user = db.relationship('User', back_populates='answers', lazy=True)

    def __repr__(self):
        return f"<Answer {self.id} to Question {self.question_id}>"


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Vote by User {self.user_id} on Question {self.question_id}>"


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comment by User {self.user_id} on Question {self.question_id}>"

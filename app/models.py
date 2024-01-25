from app import db
import base64
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    token = db.Column(db.String(32), index=True)
    token_expiration_date = db.Column(db.DateTime)
    quizzes = db.relationship('Quiz', backref="author", cascade="all, delete")
    submissions = db.relationship('Submissions', backref="user", cascade="all, delete")

    def __init__(self, **kwargs):
        # gets and generate password
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id} | {self.email} >"
    
    def check_password(self, password_guess):
        return check_password_hash(self.password, password_guess)

    def get_token(self):
        now = datetime.utcnow()

        if self.token and self.token_expiration_date > now + timedelta(minutes=10):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration_date = now + timedelta(hours=2)
        db.session.commit()
        return self.token
    
    def to_dict(self):
        
        return {
            'id': self.user_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
        }


class Quiz(db.Model):
    quiz_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    questions = db.relationship('QuizQuestion', backref='quiz', cascade="all, delete")
    submissions = db.relationship('Submissions', backref="quiz", cascade="all, delete")


class QuizQuestion(db.Model):
    question_id = db.Column(db.String, primary_key=True)
    question = db.Column(db.String, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    answers = db.relationship('QuestionAnswers', backref='question', cascade="all, delete")


class QuestionAnswers(db.Model):
    answer_id = db.Column(db.String, primary_key=True)
    question_id = db.Column(db.String, db.ForeignKey('quiz_question.question_id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    correct = db.Column(db.Boolean, nullable=False)

class Submissions(db.Model):
    submission_id = db.Column(db.Integer, primary_key=True)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    responses = db.relationship('UserResponses', backref="submission", cascade="all, delete")



class UserResponses(db.Model):
    response_id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.submission_id'), nullable=False)
    question_id = db.Column(db.String, db.ForeignKey('quiz_question.question_id'), nullable=False)
    answer_id = db.Column(db.String, db.ForeignKey('question_answers.answer_id'), nullable=False)
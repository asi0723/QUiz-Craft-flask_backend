from . import analyize
from app.models import User, QuestionAnswers, Quiz, QuizQuestion, Submissions, UserResponses
from flask import request, jsonify
from datetime import datetime
from . import api, check_json_request
from app import db
from .auth import token_auth
import sqlalchemy as sa

@analyize.route('/')
def index():
    return {
        "status": 200,
        'msg': "Programming is fun"
    }

@analyize.route('/quiz/<int:quiz_id>')
# @token_auth.login_required
def getQuizAnalytics(quiz_id: int):
    quiz = db.session.get(Quiz, quiz_id)
    if quiz:
        questions = quiz.questions
        submissions = quiz.submissions
        # responses = submissions.responses
        question_id = questions[0].question_id
        print(question_id)

        for question in questions:
            print(question.question)

        question = QuizQuestion.query.filter_by(question_id=question_id).first()

        if not question:
            return "Question not found", 404

        # Get the count of responses for each answer
        answer_counts = db.session.query(
            QuestionAnswers.text,
            sa.func.count(UserResponses.answer_id).label('response_count')
        ).join(UserResponses).filter_by(question_id=question_id).group_by(QuestionAnswers.text).all()
        print("I think the answer is", answer_counts)
        

    return {
        "hey": "Well DOne"
    }
    
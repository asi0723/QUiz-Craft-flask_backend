from werkzeug.security import generate_password_hash
from app.models import User, QuestionAnswers, Quiz, QuizQuestion, Submissions, UserResponses
from flask import request, jsonify
from datetime import datetime
from . import api, check_json_request
from app import db
from .auth import token_auth



@api.route('/')
def index():
    return "Hello World"

@api.route('/names')
def names():
    name = {'name': "APple", 'names': ["Dylan", "Craig", "Orane"], 'age': 30, 'admin': True}
    return name

# USER ROUTES


@api.route('/user')
def user():

# Create a new user
# testing endpoint
    new_user = User(
        first_name="Alice",
        last_name="Johnson",
        email="alice@examhple.com",
        password=generate_password_hash("password123")
    )
    db.session.add(new_user)
    db.session.commit()

    # Create a new quiz for the user
    new_quiz = Quiz(
        title="Science Quiz",
        description="Test your knowledge of science!",
        created_at=datetime.utcnow(),
        author=new_user
    )
    db.session.add(new_quiz)
    db.session.commit()

    # Add questions to the quiz
    questions_data = [
        {
            "question_text": "What is the chemical symbol for water?",
            "answers": [
                {"text": "H2O", "correct": True},
                {"text": "CO2", "correct": False},
                {"text": "O2", "correct": False},
                {"text": "N2", "correct": False}
            ]
        },
        {
            "question_text": "Which planet is known as the 'Red Planet'?",
            "answers": [
                {"text": "Mars", "correct": True},
                {"text": "Venus", "correct": False},
                {"text": "Jupiter", "correct": False},
                {"text": "Saturn", "correct": False}
            ]
        }
    ]

    for data in questions_data:
        # Create a new quiz question
        new_quiz_question = QuizQuestion(
            question=data["question_text"],
            quiz=new_quiz
        )
        db.session.add(new_quiz_question)
        db.session.commit()

        # Add answers to the question
        for answer_data in data["answers"]:
            new_answer = QuestionAnswers(
                text=answer_data["text"],
                correct=answer_data["correct"],
                question=new_quiz_question
            )
            db.session.add(new_answer)
            db.session.commit()

    return "Well DOne"


# QUIZ ROUTES
@api.route('/new', methods=['POST'])
@token_auth.login_required
def createQuiz():
    user = token_auth.current_user()
    check = check_json_request()
    if check:
        return check
    
    data = request.json
    requiredFields = ['title', 'description']
    missingFields = [field for field in requiredFields if field not in data]

    if missingFields:
        return {'error': f"{', '.join(missingFields)} fields are missing..."}, 400
    
    title = data.get('title')
    description = data.get('description')

    new_quiz = Quiz(title=title, description=description, author=user)

    db.session.add(new_quiz)
    db.session.commit()

    return {'msg': 'New quiz has been created', 'id': new_quiz.quiz_id}

# get al quizzes for a user
@api.route('/user-quizzes')
@token_auth.login_required
def userQuiz():
    user = token_auth.current_user()
    quizzes_data = []
    
    for quiz in user.quizzes:
        quiz_data = {
            'quiz_id': quiz.quiz_id,
            'title': quiz.title,
            'description': quiz.description,
            'author_id': quiz.user_id,
            'total_questions': len(quiz.questions),
            'submissions': len(quiz.submissions)
        }
        quizzes_data.append(quiz_data)

    return jsonify({'data': quizzes_data})

# all quizzes in database
@api.route('/all')
def getQuizzes():

    quizzes = db.session.execute(db.select(Quiz)).scalars().all()
    print("*"*30, quizzes)
    quiz_data = [{'title': quiz.title, 'description': quiz.description, 'author': {'id': quiz.author.user_id, 'first_name': quiz.author.first_name}} for quiz in quizzes]
    return jsonify(quiz_data), 200

@api.route('/questions/<int:quiz_id>', methods=['POST'])
@token_auth.login_required
def addQuestions(quiz_id):
    current_user = token_auth.current_user()
    current_quiz = db.session.execute(db.select(Quiz).where((Quiz.quiz_id == quiz_id) & (Quiz.user_id == current_user.user_id))).scalar()

    if not current_quiz:
        return {'error': 'You do not have access to read/write to this quiz'}, 403

    error = check_json_request()
    if error:
        return error, 400

    data = request.json
    print(data)
    questions = data.get('questions', [])

    for question_data in questions:
        new_question = QuizQuestion(question=question_data['question'], quiz=current_quiz)
        db.session.add(new_question)
        db.session.commit()

        answers = question_data.get('answers', [])
        print(answers)

        for answer_data in answers:
            if answer_data.get('question_id') == question_data.get('question_id'):
                new_answer = QuestionAnswers(text=answer_data['text'], correct=answer_data['correct'], question=new_question)
                db.session.add(new_answer)
                db.session.commit()


    try:
        # db.session.commit()
        return {'message': 'Questions have been added successfully'}
    except Exception as e:
        db.session.rollback()
        return {'error': f'An error occurred: {str(e)}'}, 500

# route to get all questions for a quiz
@api.route('/question/<int:quiz_id>')
# @token_auth.login_required
def getQuizQuestions(quiz_id):
    
    quiz = db.session.execute(db.select(Quiz).where(Quiz.quiz_id == quiz_id)).scalar()
    if not quiz:
        return {'error': "Quiz not found!"}, 404 
    questions = []
    for question in quiz.questions:
        incorrect_answers = []
        correct_answer = ""
        for answer in question.answers:
            if(answer.correct):
                correct_answer = answer.text
            else:
                incorrect_answers.append(answer.text)
        new_question = {
            'question': question.question,
            'correct_answer': correct_answer,
            'incorrect_answers': incorrect_answers
        }

        questions.append(new_question)

    return {'questions': questions}


# submit a quiz
@api.route('/submit/<int:quiz_id>', methods=['POST'])
@token_auth.login_required
def submitQuiz(quiz_id):

    current_user = token_auth.current_user()
    current_quiz = db.session.execute(db.select(Quiz).where(Quiz.quiz_id == quiz_id)).scalar()

    if not current_quiz:
        return {'error': "This quiz doesnt exists"}
    error = check_json_request()
    if error:
        return {'error': error}, 400
    
    data = request.json
    
    required_fields = ['score', 'responses']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} are missing"}, 400

    new_submission = Submissions(quiz=current_quiz, score = data.get('score'), user_id=current_user.user_id)

    db.session.add(new_submission)
    db.session.commit()

    responses = data.get('responses')

    for response in responses:
        question_id = response.get('question_id', None)
        answer_id = response.get('answer_id', None)

        new_response = UserResponses(question_id=question_id, answer_id=answer_id, submission=new_submission)
        db.session.add(new_response)

    db.session.commit()
    return {'success': "Submission sent thanks for completing this question"}, 200

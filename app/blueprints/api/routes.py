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

# route to delete a quiz
@api.route("/delete/<int:quiz_id>", methods=["DELETE"])
@token_auth.login_required
def delete_quiz(quiz_id):

    user = token_auth.current_user()

    quiz = Quiz.query.get(quiz_id)

    if quiz and quiz.user_id == user.user_id:
        db.session.delete(quiz)
        db.session.commit()
        return {"msg": "Quiz has been deleted successfully"}, 200
    else:
        return {"error": "This quiz wasnt found"}, 404


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
            'total_questions': len(quiz.questions),
            'submissions': len(quiz.submissions),
            'published': quiz.published
        }
        quizzes_data.append(quiz_data)

    return jsonify({'data': quizzes_data})

# all quizzes in database
@api.route('/all')
def getQuizzes():

    quizzes = db.session.execute(db.select(Quiz).where(Quiz.published == True)).scalars().all()
    print("*"*30, quizzes)
    quiz_data = []
    for quiz in quizzes:
        quiz = {
            'title': quiz.title,
            'quiz_id': quiz.quiz_id,
            'questions': len(quiz.questions),
            'submissions': len(quiz.submissions),
            'description': quiz.description,
            'author': {
                'id': quiz.author.user_id,
                'firstName': quiz.author.first_name,
                'lastName': quiz.author.last_name
                }
        }
        quiz_data.append(quiz)    
    return quiz_data, 200

# route to publish a quiz
@api.route('/publish/<int:quiz_id>', methods=["POST"])
@token_auth.login_required
def publishQuestion(quiz_id):

    quiz = db.session.get(Quiz, quiz_id)

    if(quiz):
        quiz.published = True
        db.session.commit()
        return {'success': "Quizs has been published!"}, 200
    else:
        return {'error': "This quiz cant be found"}, 404
    

# route to unpublish a quiz
@api.route('/unpublish/<int:quiz_id>', methods=["POST"])
@token_auth.login_required
def unpublishQuestion(quiz_id):

    quiz = db.session.get(Quiz, quiz_id)

    if(quiz):
        quiz.published = False
        db.session.commit()
        return {'success': "Quiz has been unpublished!"}, 200
    else:
        return {'error': "This quiz cant be found"}, 404
@api.route('/questions/add/<int:quiz_id>', methods=['POST'])
@token_auth.login_required
def add_questions(quiz_id):
    current_user = token_auth.current_user()
    current_quiz = db.session.execute(
        db.select(Quiz).where((Quiz.quiz_id == quiz_id) & (Quiz.user_id == current_user.user_id))
    ).scalar()

    if not current_quiz:
        return {'error': 'You do not have access to read/write to this quiz'}, 403

    error = check_json_request()
    if error:
        return error, 400

    data = request.json

    required_items = ['description', 'title', 'questions']
    missing_fields = [field for field in required_items if field not in data]

    if missing_fields:
        return {'error': f"{', '.join(missing_fields)}"}, 400

    update_quiz_info(current_quiz, data)

    questions = data.get('questions', [])
    update_questions(current_quiz, questions)

    return {'message': 'Questions have been added successfully'}


def update_quiz_info(quiz, data):
    description = data.get('description')
    title = data.get('title')

    quiz.description = description
    quiz.title = title
    db.session.commit()


def update_questions(quiz, questions_data):
    all_question_ids = {question.question_id for question in quiz.questions}
    incoming_ids = {question.get('id') for question in questions_data}
    new_questions = incoming_ids - all_question_ids
    questions_update = all_question_ids & incoming_ids
    questions_delete = all_question_ids - incoming_ids

    for question_data in questions_data:
        question_id = question_data['id']

        if question_id in new_questions:
            new_question = create_new_question(quiz, question_data)
            update_answers(new_question, question_data.get("answers", []))
        elif question_id in questions_update:
            update_existing_question(question_id, question_data)

    delete_questions(questions_delete)


def create_new_question(quiz, question_data):
    new_question = QuizQuestion(question_id=question_data['id'], question=question_data['question'], quiz=quiz)
    db.session.add(new_question)
    db.session.commit()
    return new_question


def update_existing_question(question_id, question_data):
    current_question = db.session.get(QuizQuestion, question_id)
    if current_question:
        current_question.question = question_data['question']
        update_answers(current_question, question_data.get('answers', []))
        db.session.commit()


def update_answers(question, answers_data):
    current_answers_ids = {answer.answer_id for answer in question.answers}
    incoming_answer_ids = {answer_data['id'] for answer_data in answers_data}

    for answer_data in answers_data:
        answer_id = answer_data['id']
        if answer_id not in current_answers_ids:
            create_new_answer(question, answer_data)
        else:
            update_existing_answer(answer_id, answer_data)
    
    delete_answers(current_answers_ids - incoming_answer_ids)


def create_new_answer(question, answer_data):
    new_answer = QuestionAnswers(answer_id=answer_data['id'], text=answer_data['text'], correct=answer_data['correct'], question=question)
    db.session.add(new_answer)


def update_existing_answer(answer_id, answer_data):
    current_answer = db.session.get(QuestionAnswers, answer_id)
    if current_answer:
        current_answer.correct = answer_data.get("correct")
        current_answer.text = answer_data.get("text")


def delete_answers(answer_ids):
    for answer_id in answer_ids:
        current_answer = db.session.get(QuestionAnswers, answer_id)
        db.session.delete(current_answer)


def delete_questions(question_ids):
    for question_id in question_ids:
        question_to_delete = db.session.get(QuizQuestion, question_id)
        db.session.delete(question_to_delete)

    db.session.commit()

# route to get all questions for a quiz
@api.route('/question/<int:quiz_id>')
# @token_auth.login_required
def getQuizQuestions(quiz_id, user_id=0):
    
    if user_id > 0:
        quiz = db.session.execute(db.select(Quiz).where((Quiz.quiz_id == quiz_id) & (Quiz.user_id == user_id))).scalar()
    else:
        quiz = db.session.execute(db.select(Quiz).where(Quiz.quiz_id == quiz_id)).scalar()

    if not quiz:
        return {'error': "Quiz not found!"}, 404 
    questions = []
    for question in quiz.questions:
        incorrect_answers = []
        correct_answer = {
            'id': 0,
            'text': ""
        }  
        for answer in question.answers:
            if(answer.correct):
                correct_answer['id'] = answer.answer_id
                correct_answer['text'] = answer.text
            else:
                incorrect_answers.append({'id': answer.answer_id, 'text': answer.text})
        new_question = {
            'question': question.question,
            'question_id': question.question_id,
            'correct_answer': correct_answer,
            'incorrect_answers': incorrect_answers
        }

        questions.append(new_question)

    return {'questions': questions, 'title': quiz.title, 'description': quiz.description}, 200

# route to get question to be edited
@api.route('/edit/<int:quiz_id>')
@token_auth.login_required
def getQuizToEdit(quiz_id):
    user = token_auth.current_user()
    user_id = user.user_id
    result, status = getQuizQuestions(quiz_id, user_id)
    return result , status


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

@api.route("/submissions/<int:quiz_id>")
@token_auth.login_required
def getSubmissions(quiz_id):
    current_user = token_auth.current_user()

    current_quiz = db.session.get(Quiz, quiz_id)
    res = []

    if current_quiz and current_user.user_id == current_quiz.user_id:
        submissions = current_quiz.submissions
        for sub in submissions:
            user = db.session.get(User, sub.user_id)
            obj = {
                "user": {
                    "firstName": user.first_name, 
                    "id": user.user_id, 
                    "lastName": user.last_name, 
                },
                "score": sub.score,
                "date_submitted": sub.date_submitted,
                "submission_id": sub.submission_id
            }
            res.append(obj)

        return res, 200
    else:
        return {"error": "Cant find quiz for this user"}, 400

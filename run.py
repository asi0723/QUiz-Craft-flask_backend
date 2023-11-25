from app import db, User, Quiz, QuizQuestion, QuestionAnswers
from datetime import datetime
from werkzeug.security import generate_password_hash

# Create a user
new_user = User(
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    password=generate_password_hash("password123", method="sha256")
)
db.session.add(new_user)
db.session.commit()

# Create a quiz for the user
new_quiz = Quiz(
    title="General Knowledge Quiz",
    description="Test your general knowledge!",
    created_at=datetime.utcnow(),
    user=new_user
)
db.session.add(new_quiz)
db.session.commit()

# Add questions to the quiz
questions_data = [
    {
        "question_text": "What is the capital of France?",
        "correct_answer_text": "Paris",
        "incorrect_answers_text": ["Berlin", "Madrid", "Rome"]
    },
    {
        "question_text": "Which planet is known as the Red Planet?",
        "correct_answer_text": "Mars",
        "incorrect_answers_text": ["Venus", "Jupiter", "Saturn"]
    }
]

for data in questions_data:
    # Create a new quiz question
    new_quiz_question = QuizQuestion(
        question=data["question_text"],
        correct_answer=None,  # Will be set later
        quiz=new_quiz
    )
    db.session.add(new_quiz_question)
    db.session.commit()

    # Create correct answer
    correct_answer = QuestionAnswers(
        text=data["correct_answer_text"],
        question=new_quiz_question
    )
    db.session.add(correct_answer)
    db.session.commit()

    # Link the correct answer to the question using correct_answer_id
    new_quiz_question.correct_answer = correct_answer
    db.session.commit()

    # Create incorrect answers
    for incorrect_answer_text in data["incorrect_answers_text"]:
        incorrect_answer = QuestionAnswers(
            text=incorrect_answer_text,
            question=new_quiz_question
        )
        db.session.add(incorrect_answer)
        db.session.commit()

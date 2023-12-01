from .auth import token_auth, basic_auth
from . import user_bp, check_json_request
from flask import request
from app.models import User
from app import db

@user_bp.route('/new', methods=['POST'])
def create_user():
    check = check_json_request()
    if check:
        return check

    # get the data from the request body
    data = request.json

    required_fields = ['firstName', 'lastName', 'email', 'password']
    missing_fields = []

    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    password = data.get('password')

    # check if user already exists
    check_user = db.session.execute(db.select(User).where((User.email == email ))).scalar()

    if check_user:
        return {'error': 'A user already registered with this email'}, 409
    
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return {'msg': "User signed up successfully"}, 201


@user_bp.route('/delete', methods=['DELETE'])
@token_auth.login_required
def deleteUser():
    user = token_auth.current_user()
    db.session.delete(user)
    db.session.commit()

    return {'msg': f"User has been deleted successfully"}, 200

@user_bp.route('/update', methods=['PUT'])
@token_auth.login_required
def updateUser():

    check = check_json_request()
    if check:
        return check
    
    optionalFields = ['firstName', 'lastName', 'email']

    data = request.json
    current_user = token_auth.current_user()
    firstName = data.get('firstName', current_user.first_name)
    lastName = data.get('lastName', current_user.last_name)
    email = data.get('email', current_user.email)

    existing_email = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if existing_email and current_user.email != email:
        return {'error': 'This email already exists'}

    current_user.first_name = firstName
    current_user.last_name = lastName
    current_user.email = email

    db.session.commit()
    return {'success': 'User has been updated'}

@user_bp.route('/login', methods=['POST'])
@basic_auth.login_required
def login():
    auth_user = basic_auth.current_user()
    if(not auth_user):
        return {'error': "Invalid Credentials"}, 401
    token = auth_user.get_token()
    user_info = auth_user.to_dict()
    result = dict({'token': token}, **user_info)
    return result , 200

@user_bp.route('/token')
@token_auth.login_required
def token():
    auth_user = basic_auth.current_user()
    user_info = auth_user.to_dict()
    
    return user_info , 200


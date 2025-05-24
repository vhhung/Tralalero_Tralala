from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.utils import api_response
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

# UC1: Register
@auth_bp.route('/register', methods=['POST'])
def register():
  data = request.get_json() or {}
  username = data.get('username')
  password = data.get('password')
  full_name = data.get('full_name')
  email = data.get('email')

  # Check username, password and email
  if User.query.filter_by(username=data['username']).first():
    return api_response(message='Username already exists', status_code=400)
  if User.query.filter_by(email=data['email']).first():
    return api_response(message='Email already exists', status_code=400)

  # Basic user profile
  try:
    user = User(
      username=data['username'],
      email=data['email'],
      fullname=data['fullname'],
    )

    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return api_response(
      message='User registered successfully',
      data={'user_id':user.id, 'username':user.username},
      status=201
    )

  except Exception as e:
    db.session.rollback()
    return api_response(message=f"Error registering user: {str(e)}", status_code=500)


# UC2: Log in
@auth_bp.route('/login', methods=['POST'])
def login():
  data = request.get_json() or {}
  username = data.get('username')
  password = data.get('password')

  user = User.query.filter_by(username=data['username']).first()
  if not user or not user.check_password(data['password']):
    return api_response(message='Invalid username or password', status_code=401)

  # If both username and password are correct, then create an access token and a refresh token
  access_token = create_access_token(identity=str(user.id))
  refresh_token = create_refresh_token(identity=str(user.id))

  # Return the 'Success' response wither token and user's information
  return api_response(
    message='Login successful',
    data = {
      'access_token' : access_token,
      'refresh_token' : refresh_token,
      'user' : user.to_dict()
    })

# UC3: Log out
@auth_bp.route('/logout', methods=['POST'])
def logout():
  return api_response(message="Logout successful")
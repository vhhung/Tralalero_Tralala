from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.models.user import User

# Api response function
def api_response(data=None, message=None, status=200):
  response={
    'success' : 200 <= status < 300,
    'status' : status
  }
  if message:
    response['message'] = message
  
  if data is not None:
    response['data'] = data
  
  return jsonify(response), status    

# Implementation of token_required Decorator
def token_required(fn):
  @wraps(fn)
  def wrapper(*args, **kwargs):
    try:
      # Verify the JWT token in the request headers
      verify_jwt_in_request()
      # Get username (identity) from JWT token
      user_id = get_jwt_identity()
      # Get user's name from database
      current_user = User.query.get(user_id)

      # Check the existence of user
      if not current_user:
        return api_response(message="User does not exist", status=404)

      # Invoke the original endpoint, passing the information of authenticated user
      return fn(current_user, *args, **kwargs)
    except Exception as e:
      # If there is an error during token validation
      return api_response(message=f"Token is invalid: {str(e)}", status=401)
  return wrapper
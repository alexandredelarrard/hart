from flask import request, jsonify
import logging

from flask_cors import  cross_origin
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies

from . import authorization_blueprint
from src.schemas.user import User
from src.extensions import front_server

# =============================================================================
# authentification
# =============================================================================
@authorization_blueprint.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(origin=front_server)
def login():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'Options request handled'}), 200
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            access_token = create_access_token(identity={'email': user.email})
            return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
       
# Route to handle logout
@authorization_blueprint.route('/logout', methods=['POST'])
@cross_origin(origin=front_server)
@jwt_required()
def logout():
    response = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(response)
    return response, 200

# Route to check if user is logged in
@authorization_blueprint.route('/protected', methods=['GET'])
@cross_origin(origin=front_server)
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

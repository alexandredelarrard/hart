from flask import request, jsonify, url_for
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_mail import Message
from itsdangerous import SignatureExpired
from flask_cors import cross_origin
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, 
    unset_jwt_cookies, set_access_cookies, set_refresh_cookies
)

from . import authorization_blueprint
from .utils import confirmation_email_html, reset_email_html
from src.schemas.user import User
from src.schemas.payment import PaymentTrack
from src.extensions import db, mail, serializer, front_server, config

# =============================================================================
# Authentication
# =============================================================================
@authorization_blueprint.route('/login', methods=['POST'])
@cross_origin(origins=front_server)
def login():
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity={'email': user.email})
            refresh_token = create_refresh_token(identity={'email': user.email})
            response = {
                'message': 'Login successful', 
                'access_token': access_token,
                'refresh_token': refresh_token,
                'userdata': user.to_dict()}
            
            last_payment = PaymentTrack.query.filter_by(user_id=user.id).order_by(desc(PaymentTrack.plan_start_date)).first()
            if last_payment:
                response["plan_name"] = last_payment.plan_name
                response["plan_end_date"] = last_payment.plan_end_date.isoformat()
                response["remaining_closest_volume"] = last_payment.remaining_closest_volume
                response["remaining_search_volume"] = last_payment.remaining_search_volume

            response = jsonify(response)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response, 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

# Route to handle logout
@authorization_blueprint.route('/logout', methods=['POST'])
@cross_origin(origins=front_server)
@jwt_required()
def logout():
    response = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(response)
    return response, 200

# Route to check if user is logged in
@authorization_blueprint.route('/protected', methods=['GET'])
@cross_origin(origins=front_server)
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@authorization_blueprint.route('/refresh', methods=['POST'])
@cross_origin(origins=front_server)
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    response = jsonify({'access_token': access_token})
    set_access_cookies(response, access_token)
    return response, 200

@authorization_blueprint.route('/signin', methods=['POST'])
@cross_origin(origins=front_server)
def signin():
   
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('username')
        surname = data.get('surname')
        job = data.get('metier')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if len(password) > 20:
            return jsonify({'error': 'Password should have fewer than 20 characters'}), 401

        user = User.query.filter_by(email=email).first()

        if user:
            return jsonify({'error': 'Email already in use'}), 404
        
        else:
            try:

                # create new user 
                hashed_password = generate_password_hash(password)
                new_user = User(
                    email=email,
                    password=hashed_password,
                    name=name,
                    surname=surname,
                    job=job,
                    creation_date=datetime.today().strftime("%Y-%m-%d %H:%M"),
                    email_confirmed=False,
                    active=True,
                    plan="free"
                )
                db.session.add(new_user)
                db.session.commit()
                
                # create new payment line  
                payment = PaymentTrack(
                    user_id=new_user.id,
                    paying_date= datetime.today(),
                    # paying_methode="FREE",
                    payment_amount=0,
                    plan_name=config.plans["free"],
                    plan_frequency="monthly",
                    plan_start_date=datetime.today(),
                    plan_end_date=datetime.today() + timedelta(days=config.product["free_plan_days"]),
                    initial_closest_volume=config.product["initial_closest_volume"],
                    remaining_closest_volume=config.product["initial_closest_volume"],
                    initial_search_volume=config.product["initial_search_volume"],
                    remaining_search_volume=config.product["initial_search_volume"]
                )
                db.session.add(payment)
                db.session.commit()

                # Generate a token
                token = serializer.dumps(email, salt='email-confirm')

                # Send confirmation email
                try:
                    confirm_url = url_for('authorization.confirm_email', token=token, _external=True)
                    html = confirmation_email_html(new_user, confirm_url)
                    msg = Message('Artyx: Confirmation de votre email', recipients=[email], html=html)
                    mail.send(msg)
                except Exception as e:
                    print(f"could not send email {e}")

                access_token = create_access_token(identity={'email': new_user.email})
                refresh_token = create_refresh_token(identity={'email': new_user.email})
                response = jsonify({
                    'message': 'Signin successful', 
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'userdata': new_user.to_dict()
                })
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                return response, 200
            
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': 'Failed to create user', 'details': str(e)}), 500

@authorization_blueprint.route('/confirm/<token>', methods=['GET'])
@cross_origin(origins=front_server)
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        user = User.query.filter_by(email=email).first_or_404()
        
        # Update the user as confirmed
        user.email_confirmed = True
        db.session.commit()
        
        return jsonify({'message': 'Email confirmed. You can now log in.'}), 200
    except SignatureExpired:
        return jsonify({'error': 'The confirmation link has expired.'}), 400

@authorization_blueprint.route('/reset-password', methods=['POST'])
@cross_origin(origins=front_server)
def reset_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    
    if user:
        token = serializer.dumps(email, salt='password-reset-salt')
        reset_url = url_for('authorization.set_new_password', token=token, _external=True)
        html = reset_email_html(user, reset_url)
        msg = Message('Artyx: Réinitialisation du mot de passe', recipients=[email], html=html)
        mail.send(msg)
        return jsonify({'message': 'A password reset link has been sent to your email.'}), 200
    return jsonify({'error': 'Email not found'}), 404


@authorization_blueprint.route('/set-new-password/<token>', methods=['POST'])
@cross_origin(origins=front_server)
def set_new_password(token):
    if request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        
        try:
            email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash(password)
                db.session.commit()
                return jsonify({'message': 'Your password has been updated.'}), 200
        except SignatureExpired:
            return jsonify({'error': 'The password reset link has expired.'}), 400

        return jsonify({'error': 'Invalid token'}), 400
    
    
@authorization_blueprint.route('/update-user-profile', methods=['POST'])
@cross_origin(origins=front_server)
@jwt_required()
def update_user_profile():
    if request.method == 'POST':
        data = request.get_json()

        email = get_jwt_identity()['email']
        name = data.get('name')
        surname = data.get('surname')
        address = data.get('address')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            try:
                user.name = name
                user.surname = surname
                user.address = address  
                db.session.commit()

                return jsonify({'message': 'Your infos have been updated.'}), 200
            except Exception:
                return jsonify({'error': 'The update could not be performed.'}), 400

        return jsonify({'error': 'User not found'}), 500
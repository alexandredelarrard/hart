from flask import Blueprint, request, jsonify, abort
import flask_praetorian
import os 
from itsdangerous import URLSafeTimedSerializer

from ..utils.models import mongo, guard, configs

logger = configs.logger

blueprint_auth = Blueprint('blueprint_auth', __name__)
ts = URLSafeTimedSerializer(os.environ["SECRET_KEY"])


# =============================================================================
# authentification
# =============================================================================
@blueprint_auth.route('/signup', methods=['POST'])
def signup_post():

    error=""
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # if this returns a user, then the email already exists in database
        user = mongo.db.user_front.find_one({"email" : email})

        if user is not None:
            error = f'{email} est déjà utilisé'
            # new_user=user

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        if error == "":
            new_user = mongo.db.user_front.insert({"name":"", 
                                                  "surname":"",
                                                  "username": username,
                                                  "email" : email,
                                                  "password" : guard.hash_password(password),
                                                  "is_active" : False,
                                                  "validated" : False, 
                                                  "roles" : "user"})
            
            #  create token for email to validate 
            # token_email = ts.dumps(email, salt='email-confirm-key')

            ret = {"accessToken" : guard.encode_jwt_token(new_user),
                    # "token_email" : token_email,
                    "id" : new_user.id,
                    "email": new_user.email,
                    "message" : "Un e-mail de confirmation à été envoyé sur votre adresse email : plus qu'à le valider :)",
                    "username" : new_user.username,
                    "roles" : new_user.roles.split(",")}

            print(ret, flush=True)
            return jsonify(ret), 200
        else:
            return jsonify({"message" : error}), 404

    else:
        return jsonify({"message" : "ONLY POST IMPLEMENTED FOR SIGNUP METHOD"}), 401


@blueprint_auth.route('/signup/confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)

    except Exception as e:
        abort(404)

    if email:
        user = user_front.query.filter_by(email=email).first_or_404()
        user.email_validated = True
        db.session.add(user)
        db.session.commit()

        return jsonify({"message" : "Félicitation, nous venons de valider votre email !"}), 200
    
    else:
        return jsonify({"message" : "Email non validé"}), 401


@blueprint_auth.route('/signin', methods=['POST'])
def login_post():

    ret = {"accessToken" : "",
          "id" : "",
          "error" : ""}

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = mongo.db.user_front.find_one({"email" : email})

        if user:
            user_username = user.username
            user = guard.authenticate(user_username, password)

            if not user:
                error = "Mot de passe non valide"
                return jsonify({"message" : error}), 404

            ret = guard.encode_jwt_token(user)
            ret = {"accessToken" : guard.encode_jwt_token(user),
                    "id" : user.id,
                    "email": user.email,
                    "username" : user.username,
                    "roles" : user.roles.split(",")}

            # give all info on user
            for key in ["name", "surname"]:
                if eval(f"user.{key}") != "":
                    ret[key] = eval(f"user.{key}")
            
            return jsonify(ret), 200
        else:
            error = "email non trouvé"
            return jsonify({"message" : error}), 404

    return jsonify({"message" : "OUT POST SIGNIN"}), 401


@blueprint_auth.route('/refresh', methods=['POST'])
def refresh():
    """
    Refreshes an existing JWT by creating a new one that is a copy of the old
    except that it has a refrehsed access expiration.
    """ 
    if request.method == 'POST':
        print("refresh request", flush=True)
        old_token = request.get_data()
        new_token = guard.refresh_jwt_token(old_token)
        ret = {'accessToken': new_token}
        return ret, 200


@blueprint_auth.route('/protected')
@flask_praetorian.auth_required
def protected():
    """
    A protected endpoint. The auth_required decorator will require a header
    containing a valid JWT
    .. example::
       $ curl http://localhost:5000/api/protected -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    return {'message': f'protected endpoint (allowed user {flask_praetorian.current_user().username})'}


@blueprint_auth.route('/email_lost', methods=['POST'])
def email_lost_post():
    if request.method == 'POST':
        security_question = request.form.get('security_question').lower().strip()
        user = mongo.db.user_front.find_one({"security" : security_question})

        if user is not None:
            good = f"Nous avons envoyé un email de réinitialisation sur votre email"

            temporary_password = str(uuid.uuid4()).replace('-','')

            mongo.db.user_front.find_one_and_update(
					{"security" : security_question},
					{"$set":
						{"email_validated": False,
                        "password" : generate_password_hash(temporary_password, method='sha256')}
					}, upsert=True
				)

            confirm_email_sent(user, temporary_password)

            return jsonify(error="", message=good), 200

        else:
            error = "Votre réponse n'est pas correcte. Veuillez réessayer"
            return jsonify(error=error), 200
    else:
        return jsonify(error="ONLY POST IMPLEMENTED FOR RESET PASSWORD METHOD"), 400


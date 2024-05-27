import os 
from flask_mail import Message
from flask import render_template, url_for
from itsdangerous import URLSafeTimedSerializer
from ..utils.models import mail

def confirm_email_sent(user, temporary_password):

    subject = "Valider votre email"

    ts = URLSafeTimedSerializer(os.environ["SECRET_KEY"])
    token = ts.dumps(user.email, salt='email-confirm-key')

    confirm_url = url_for('blueprint_auth.confirm_email',
                           token=token,
                           _external=True)

    html = render_template('activate.html',
                            confirm_url=confirm_url,
                            username=user.username,
                            password=temporary_password)

    send_email(user.email, subject, html)


def resend_password_sent(user, temporary_password):
    subject = "Votre nouveau mot de passe"
    html = render_template('new_password.html',
                            username=user.username,
                            password=temporary_password)
    send_email(user.email, subject, html)


def send_email(email, subject, html):

    with mail.connect() as conn:
        msg = Message(subject=subject,
                      sender= "Alexandre de Covital <" + os.environ["MAIL_USERNAME"] + ">",
                      recipients=[email])
       
        print(os.environ["MAIL_USERNAME"])
        msg.html = html
        conn.send(msg)
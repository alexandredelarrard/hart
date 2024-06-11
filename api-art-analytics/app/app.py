from flask import Flask
import os
from src.blueprints.authorization import authorization_blueprint
from src.blueprints.retreiver_infos import infos_blueprint
from src.utils.step import Step
from src.extensions import config, context

class App(Step):

	def __init__(self, config, context):
		super().__init__(config=config, context=context)

	#Flask application factory
	def create_app(self):

		# Initialize the core application.
		app = Flask(__name__, instance_relative_config=True)
		app = self.set_config_app(app)

		# Initialize db and mail connected to app
		self._context.flask_db.init_app(app)
		self._context.mail_con.init_app(app)
		self._context.jwt.init_app(app)
		self._context.cors.init_app(app)

		# Import parts of our application
		app.register_blueprint(authorization_blueprint, url_prefix="/")
		app.register_blueprint(infos_blueprint, url_prefix="/")

		return app

	def set_config_app(self, app):
			
		app.config["SQLALCHEMY_DATABASE_URI"] = self._context.connexion_string
		app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
		app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
		app.config['CORS_HEADERS'] = 'Content-Type'
		app.config["JWT_ACCESS_LIFESPAN"] = {'hours': 3}
		app.config["JWT_REFRESH_LIFESPAN"] = {'days': 1}
		app.config['SECRET_KEY'] = os.environ["SECRET_KEY_LOGIN"]
		app.config["DEBUG"] = False
		app.config["TESTING"] = False
		app.config.update(self._context.email_config)

		return app
	
app_step = App(config=config, context=context)
app = app_step.create_app()

if __name__ == "__main__":
	app.run(debug=False, host="0.0.0.0", port=8888)	

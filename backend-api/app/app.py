from flask import Flask
from celery import Celery

from src.blueprints.closest import closest_blueprint
from src.utils.step import Step
from src.extensions import config, context

class App(Step):

	def __init__(self, config, context):
		super().__init__(config=config, context=context)

	#Flask application factory
	def create_app(self):

		# Initialize the core application.
		app = Flask(__name__, instance_relative_config=True)
		app = self.set_config_app(app, debug=True)

		# Initialize db and mail connected to app
		self._context.flask_db.init_app(app)
		self._context.cors.init_app(app)

		# Import parts of our application
		app.register_blueprint(closest_blueprint, url_prefix="/")

		return app

	def set_config_app(self, app, debug=True):
			
		app.config["CELERY_BROKER_URL"] = self._config.celery.url
		app.config["CELERY_RESULT_BACKEND"] = self._config.celery.url
		app.config["SQLALCHEMY_DATABASE_URI"] = self._context.connexion_string
		app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
		app.config["CORS_HEADERS"] = "Content-Type"

		if debug:
			app.config["DEBUG"] = True
			app.config["TESTING"] = True
		else:
			app.config["DEBUG"] = False
			app.config["TESTING"] = False

		return app
		
	def make_celery(self, app):
		celery = Celery(
			app.import_name,
			broker=app.config['CELERY_BROKER_URL'],
			broker_connection_retry_on_startup=True
		)
		celery.conf.update(app.config)
		return celery

# accessible variables
app_step = App(config=config, context=context)
app = app_step.create_app()
celery = app_step.make_celery(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask
from py_scripts.utils.models import configs, mongo, mail, guard, User
  
#Flask application factory
def create_app():

	# Initialize the core application.
	app = Flask(__name__, instance_relative_config=True, template_folder='./front_templates')
	app = configs.set_config_app(app, debug=True)

	# Initialize db and mail connected to app
	guard.init_app(app, User)
	mongo.init_app(app) 
	mail.init_app(app)

	with app.app_context():    
		import py_scripts.utils.models

	# Import parts of our application
	from py_scripts.front.articles import blueprint_articles as blueprint_articles
	app.register_blueprint(blueprint_articles, url_prefix ="/")  

	from py_scripts.front.authorizations import blueprint_auth as blueprint_auth
	app.register_blueprint(blueprint_auth, url_prefix="/")

	return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8008)

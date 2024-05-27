from flask import request, jsonify, make_response, Blueprint
from bson.objectid import ObjectId
from ..utils.models import mongo, configs

logger = configs.logger
blueprint_articles = Blueprint('blueprint_articles', __name__)

@blueprint_articles.route('/', methods=['GET'])
def get_all_articles_headers():

	domains = ["economie", "sante", "education", "media", "politiciens"]

	users = mongo.db.new_text.find({"domain":{"$in":domains}})

	answer = []
	for user in users: 
		try: 
			answer.append({
			"_id" : str(user['_id']),
			'domain' : user['domain'], 
			'h1' : user['h1'], 
			'author' : user['author'],
			"time" : user['time'],
			"like": user["like"],
			"summary" : user['summary']})
		except Exception as e:
			logger.warning(e)
			pass

	response = make_response(jsonify({"articles" : answer}), 200)

	return response

# Import parts of our application
@blueprint_articles.route('/<domain>', methods=['GET'])
def get_articles_headers(domain):

	users = mongo.db.new_text.find({"domain": domain})
	answer = [{
			"_id" : str(user['_id']),
			'domain' : user['domain'], 
			'h1' : user['h1'], 
			'author' : user['author'],
			"time" : user['time'],
			"summary" : user['summary'],
			"like": user["like"],
			"article_body" : user['article_body']} for user in users]

	response = make_response(jsonify({"articles" : answer}), 200)

	return response

# Import parts of our application
@blueprint_articles.route('/<domain>/<_id>', methods=['GET'])
def get_article(domain, _id):

	users = mongo.db.new_text.find({"domain": domain, "_id" : ObjectId(_id)})
	answer = [{
			"_id" : str(user['_id']),
			'domain' : user['domain'], 
			'h1' : user['h1'], 
			'author' : user['author'],
			"time" : user['time'],
			"summary" : user['summary'],
			"like": user["like"],
			"article_body" : user['article_body']} for user in users]

	response = make_response(jsonify({"articles" : answer}), 200)

	return response

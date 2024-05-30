from src.context import get_config_context

# get config context & co 
config, context = get_config_context(config_path="./configs", 
									 use_cache = False, 
									 save=False)

db = context.flask_db
front_server= config.front_end.server

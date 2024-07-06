from src.context import get_config_context

config, context = get_config_context(
    config_path="./configs", use_cache=False, save=False
)
serializer = context.serializer
mail = context.mail_con
db = context.flask_db
jwt = context.jwt
front_server = config.front_end.server

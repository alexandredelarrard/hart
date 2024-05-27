import flask_praetorian
from configs.configs import Config
from mongoengine import Document, fields, DoesNotExist, signals
from bson.json_util import loads, dumps

configs = Config("./configs")
mongo, mail = configs.init_db()
guard = flask_praetorian.Praetorian()

allowed_roles = ["admin", "user"]

class RoleException(Exception):
    pass

class User(Document):
    """
    This is a small sample of a User class that persists to MongoDB.
    The following docker-compose.yml snippet can be used for testing.
    Please do not use in production.
    version: "3.2"
    services:
    mongo:
        image: mongo:latest
        container_name: "mongo"
        restart: always
        ports:
        - 27017:27017
    """

    username = fields.StringField(required=True, unique=True)
    password = fields.StringField(required=True)
    roles = fields.StringField()
    is_active = fields.BooleanField(default=True)

    @classmethod
    def lookup(cls, username):
        try:
            return User.objects(username=username).get()
        except DoesNotExist:
            return None

    @classmethod
    def identify(cls, id):
        try:
            return User.objects(id=loads(id)).get()
        except DoesNotExist:
            return None

    @property
    def rolenames(self):
        try:
            return self.roles.split(",")
        except RoleException:
            return []

    @property
    def identity(self):
        return dumps(self.id)

    @property
    def password(self):
        return dumps(self.password)

    def is_valid(self):
        return self.is_active

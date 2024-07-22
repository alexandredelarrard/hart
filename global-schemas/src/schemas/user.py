from src.extensions import db


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    job = db.Column(db.String(120), nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    creation_date = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=False)
    plan = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name != "password"
        }

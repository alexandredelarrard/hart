from src.extensions import db

class Experts(db.Model):
    __tablename__ = 'experts'
    __table_args__ = {'extend_existing': True}
    id_expert = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expert_surname = db.Column(db.String(120), nullable=False)
    expert_surname = db.Column(db.String(120), nullable=False)
    expert_gender = db.Column(db.String(2), nullable=False)
    expert_cellphone = db.Column(db.String(15), nullable=False)
    expert_email = db.Column(db.String(100), nullable=False)
    expert_zipcode = db.Column(db.String(15), nullable=False)
    expert_city= db.Column(db.String(255), nullable=False)
    expert_longitude = db.Column(db.Float, nullable=False)
    expert_latitude = db.Column(db.Float, nullable=False)
    expert_grade = db.Column(db.Integer, nullable=False)
    expert_expertise = db.Column(db.String(255), nullable=False)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
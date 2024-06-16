from src.extensions import db

class PaymentTrack(db.Model):
    __tablename__ = 'payment_track'
    __table_args__ = {'extend_existing': True}
    payment_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    paying_date = db.Column(db.DateTime, nullable=True)
    paying_methode = db.Column(db.String(120), nullable=True)
    plan_name = db.Column(db.String(120), nullable=True)
    plan_frequency = db.Column(db.String(120), nullable=True)
    plan_start_date = db.Column(db.DateTime, nullable=True)
    plan_end_date = db.Column(db.DateTime, nullable=True)
    initial_closest_volume = db.Column(db.Integer, nullable=True)
    remaining_closest_volume = db.Column(db.Integer, nullable=True)
    initial_search_volume = db.Column(db.Integer, nullable=True)
    remaining_search_volume = db.Column(db.Integer, nullable=True)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
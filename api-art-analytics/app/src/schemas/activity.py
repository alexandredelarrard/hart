from src.extensions import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    __table_args__ = {'extend_existing': True}
    activity_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    user_email = db.Column(db.String(120), nullable=False)
    activity_type = db.Column(db.String(80), nullable=False)
    activity_details = db.Column(db.String(255), nullable=True)
    activity_timestamp = db.Column(db.String(255), nullable=False)
    machinespecs = db.Column(db.String(255), nullable=True)
    geolocalisation = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'activity_id': self.activity_id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'activity_type': self.activity_type,
            'activity_details': self.activity_details,
            'activity_timestamp': self.activity_timestamp,
            'geolocalisation': self.geolocalisation
        }
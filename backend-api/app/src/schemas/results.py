from src.extensions import db

class CloseResult(db.Model):
    __tablename__ = 'closeresult'
    __table_args__ = {'extend_existing': True}
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.String(120), nullable=False)
    text = db.Column(db.String(10000), nullable=False)
    file = db.Column(db.String(10000), nullable=False)
    creation_date = db.Column(db.String(120), nullable=False)
    closest_ids = db.Column(db.String(99000), nullable=False)
    closest_distances= db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    result_date = db.Column(db.String(120), nullable=False)
    visible_item = db.Column(db.Boolean, nullable=False)
    llm_result = db.Column(db.String(10000), nullable=False)

    def to_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

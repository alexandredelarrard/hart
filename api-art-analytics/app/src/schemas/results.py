from src.extensions import db
import base64

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

    def to_dict(self):
        return {
            'result_id': self.result_id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'status': self.status,
            'closest_distances': self.closest_distances,
            'closest_ids': self.closest_ids,
            'file': base64.b64encode(self.file.encode(encoding="utf-8")).decode('utf-8'),
            'text': self.text,
            "result_date": self.result_date,
            "visible_item": self.visible_item,
        }
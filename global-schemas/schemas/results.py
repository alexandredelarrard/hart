from src.extensions import db
import ast


class CloseResult(db.Model):
    __tablename__ = "closeresult"
    __table_args__ = {"extend_existing": True}
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.String(120), nullable=False)
    text = db.Column(db.String(10000), nullable=False)
    file = db.Column(db.String(10000), nullable=False)
    creation_date = db.Column(db.String(120), nullable=False)
    answer = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(120), nullable=False)
    result_date = db.Column(db.String(120), nullable=False)
    visible_item = db.Column(db.Boolean, nullable=False)
    llm_result = db.Column(db.String(10000), nullable=False)

    def to_dict(self):
        return {
            "result_id": self.result_id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "status": self.status,
            "answer": self.answer,
            "file": self.file,
            "text": self.text,
            "result_date": self.result_date,
            "visible_item": self.visible_item,
            "llm_result": (
                ast.literal_eval(self.llm_result) if self.llm_result else None
            ),
        }

from db import db

class ListLikeModel(db.Model):
    __tablename__ = "listlike"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'))

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

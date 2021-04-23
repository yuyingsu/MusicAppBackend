from db import db

class FriendShipModel(db.Model):
    __tablename__ = "friendship"

    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    user1_name = db.Column(db.String(80), nullable=False)
    user2_name = db.Column(db.String(80), nullable=False)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

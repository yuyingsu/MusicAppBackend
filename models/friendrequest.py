from db import db

class FriendRequestModel(db.Model):
    __tablename__ = "friendrequest"
    id = db.Column(db.Integer, primary_key=True)

    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_user_name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(80), default="pending", nullable=False)
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

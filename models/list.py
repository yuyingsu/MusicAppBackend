from db import db
from models.listlike import ListLikeModel
from models.song import SongModel, lists_songs

class ListModel(db.Model):
    __tablename__ = "list"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80))    

    #each list belongs to one user, one user can have multiple lists. (One-To-Many Relationship)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    
    likes = db.relationship('ListLikeModel', backref='list', lazy='dynamic')

    songs = db.relationship(
        'SongModel', secondary=lists_songs, backref='song', lazy='dynamic')

    @classmethod
    def find_by_id(cls, _id: int) -> "ListModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> "ListModel":
        return cls.query.filter_by()
    

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

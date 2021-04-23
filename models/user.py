from requests import Response
from flask import request, url_for
from models.address import AddressModel
from models.list import ListModel
from models.listlike import ListLikeModel
from models.song import SongModel
from models.friendship import FriendShipModel
from models.friendrequest import FriendRequestModel
from werkzeug.security import check_password_hash
from datetime import datetime
from db import db

association = db.Table(
    "users_events",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("event_id", db.Integer, db.ForeignKey("event.id")),
)

class UserModel(db.Model):
    __tablename__ = "user" 

    id = db.Column(db.Integer, primary_key=True)
    isVerified = db.Column(db.Boolean, nullable=False, default=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    bio = db.Column(db.String(200))
    
    #one user has one address, each address belongs to one user(One-to-One Relationship)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'),
        nullable=True)

    #one user has many lists, each list belongs to one user(One-to-Many Relationship)
    lists = db.relationship(
        "ListModel", backref='user', lazy=True, cascade="all, delete-orphan"
    )

    #one user takes part in many events, each event accommodates many users(Many-to-Many Relationship) 
    events = db.relationship(
        'EventModel', secondary=association, back_populates="users"
    )

    #each listlike consists of a pair of user_id and list_id. each user can like multiple lists(Many-to-Many Relationship)
    likes = db.relationship(
        'ListLikeModel', backref='user', lazy='dynamic')

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def verify_hash(self,password):
        return check_password_hash(self.password,password)

    def sign_up_event(self, event_id):
        if not self.has_signed_up_event(event_id):
            event = EventModel.find_by_id(event_id)
            event.users.append(self)
            self.save_to_db()
            return True
        else:
            return False
    
    def undo_sign_up(self, event_id):
        if self.has_signed_up_event(event_id):
            event = EventModel.find_by_id(event_id)
            event.users.remove(self)
            print(event.users)           
            self.save_to_db()
            return True
        else:
            return False

    def has_signed_up_event(self, event_id):
        users = EventModel.find_by_id(event_id).users
        for user in users:
            if user.id == self.id:
                return True 
        return False

    def like_list(self, list_id):
        if not self.has_liked_list(list_id):
            like = ListLikeModel(user_id=self.id, list_id=list_id)
            like.save_to_db()
            return True
        else:
            return False

    def unlike_list(self, list_id):
        if self.has_liked_list(list_id):
            ListLikeModel.query.filter_by(
                user_id=self.id,
                list_id=list_id).first().delete_from_db()
            return True
        else:
            return False
            

    def has_liked_list(self, list_id):
        return ListLikeModel.query.filter(
            ListLikeModel.user_id == self.id,
            ListLikeModel.list_id == list_id).count() > 0
    
    def send_request(self, user_id):
        if not self.has_sent_request(user_id):
            fq = FriendRequestModel(from_user_id=self.id, to_user_id=user_id, from_user_name=self.username, date=datetime.now())
            fq.save_to_db()
            return True
        else:
            return False

    def has_sent_request(self, user_id):
        return FriendRequestModel.query.filter(
            FriendRequestModel.from_user_id == self.id,
            FriendRequestModel.to_user_id == user_id).count() > 0

    def accept_request(self, user_id):
         fq = FriendRequestModel.query.filter_by(from_user_id=user_id, to_user_id=self.id).first()
         fq.status = "accepted"
         friend = UserModel.find_by_id(user_id)
         friendship = FriendShipModel(user1_id=self.id, user2_id=user_id, user1_name=self.username, user2_name=friend.username)
         friendship.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class EventModel(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    #each event takes part in one address. each address can hold multiple events at different times.(One-to-Many Relationship)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'),
        nullable=False)

    users = db.relationship(
        'UserModel', secondary=association, back_populates="events"
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
        
    @classmethod
    def find_by_id(cls, _id: int) -> "EventModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> "EventModel":
        return cls.query.filter_by()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
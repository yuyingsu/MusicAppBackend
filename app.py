import eventlet
from eventlet import wsgi
from flask_mail import Mail
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from marshmallow import ValidationError
from flask_uploads import configure_uploads, patch_request_class
from flask_rest_paginate import Pagination
from libs.image_helper import IMAGE_SET
from dotenv import load_dotenv
from flask_socketio import SocketIO, send, emit, join_room
from flask import session, request
from db import db
from ma import ma
from blacklist import BLACKLIST

app = Flask(__name__)
db.init_app(app)
migrate = Migrate(app, db)
pagination = Pagination(app, db)
load_dotenv(".env", verbose=True)
app.config.from_object("config")  # load default configs from config.py
app.config.from_envvar(
    "APPLICATION_SETTINGS"
)  # override with config.py (APPLICATION_SETTINGS points to config.py)
patch_request_class(app, 10 * 1024 * 1024)  # restrict max upload image size to 10MB
configure_uploads(app, IMAGE_SET)
api = Api(app)
mail = Mail(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

socketIo = SocketIO(app, cors_allowed_origins="*")

users = {}

@socketIo.on("connect")
def on_connect():
    print("User Connected!")

@socketIo.on("online_friends")
def send_users():
    print(users.keys())
    emit('users', {'users': list(users.keys())}, broadcast=True)

@socketIo.on("join_chat")
def join_chat(username):
    users[username]=request.sid
    print('{} join chat.'.format(username))

@socketIo.on('private_message')
def private_message(payload):
    recipient_session_id = users[payload['from']]
    self_session_id = users[payload['to']]
    data = {}
    data['message'] = payload['message']
    data['from'] = payload['from']
    data['to'] = payload['to']
    print(data)
    emit('new_private_message', data, room=recipient_session_id)
    emit('new_private_message', data, room=self_session_id)

@socketIo.on('leave_chat')
def leave_chat(username):
    del users[username]
    emit('users', {'users':list(users.keys())}, broadcast = True)  

jwt = JWTManager(app)

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST

from resources.user import (
    UserRegister, UserConfirm, UserLogin, UserLogout, GetUserBio, 
    UpdateUserBio, LikeList, UnlikeList, LikedList,ListByMember,
    GetUserProfile, SignUpEvent, GetLikedList, ResendConfirmation,
    UndoSignUpEvent
    )
from resources.address import Address, GetAddress
from resources.list import List, ListsList, ManageList, GetUserLike, Recommendate
from resources.image import AvatarUpload, Avatar
from resources.event import Event, EventsList, GetEvent, RecommendateEvents, GetEventByUser, IsAttended
from resources.friendrequest import SendRequest, HasSentRequest, AcceptRequest, PendingRequests
from resources.friendship import FriendLists

api.add_resource(UserRegister, "/register")
api.add_resource(UserConfirm, "/confirm/<token>")
api.add_resource(UserLogin, "/signin")
api.add_resource(UserLogout, "/signout")
api.add_resource(GetUserBio, "/userbio/<int:user_id>")
api.add_resource(UpdateUserBio, "/updatebio/<int:user_id>")
api.add_resource(LikeList, "/like/<int:list_id>")
api.add_resource(UnlikeList, "/unlike/<int:list_id>")
api.add_resource(LikedList, "/liked/<int:list_id>")
api.add_resource(GetUserProfile, "/userprofile/<int:user_id>")
api.add_resource(SignUpEvent, "/signup/<int:event_id>")
api.add_resource(UndoSignUpEvent, "/undosignup/<int:event_id>")
api.add_resource(Recommendate, "/recommendate/<int:user_id>")
api.add_resource(RecommendateEvents, "/recommendateevent/<int:user_id>")

api.add_resource(ResendConfirmation, "/reconfirm")

api.add_resource(SendRequest, "/sendrequest/<int:to_user_id>")
api.add_resource(HasSentRequest, "/hassentrequest/<int:to_user_id>")
api.add_resource(AcceptRequest, "/acceptrequest/<int:from_user_id>")
api.add_resource(PendingRequests, "/pendingrequests")

api.add_resource(FriendLists, "/friendlist")

api.add_resource(Address, "/createaddress")
api.add_resource(GetAddress, "/address/<int:id>")

api.add_resource(List, "/createlist")
api.add_resource(ListsList, "/alllists/<int:page>")
api.add_resource(ManageList, "/list/<int:list_id>")
api.add_resource(GetUserLike, "/likedlist/<int:list_id>")
api.add_resource(ListByMember, "/mylist")
api.add_resource(GetLikedList, "/mylike/<int:user_id>")

api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")

api.add_resource(Event, "/createevent")
api.add_resource(EventsList, "/events/<int:page>")
api.add_resource(GetEvent, "/event/<int:id>")
api.add_resource(GetEventByUser, "/signedupevents/<int:user_id>")
api.add_resource(IsAttended, "/isattended/<int:event_id>")

cors = CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    ma.init_app(app)
    socketio.run(app)

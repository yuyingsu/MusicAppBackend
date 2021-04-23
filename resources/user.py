from flask_restful import Resource
from flask import url_for
from flask import Response
from flask import request
from flask import render_template_string
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from werkzeug.security import generate_password_hash
from models.user import UserModel
from models.listlike import ListLikeModel
from models.list import ListModel
from models.user import EventModel
from schemas.user import UserSchema
from schemas.list import ListSchema 
from blacklist import BLACKLIST
from libs.strings import gettext
from libs.token import ( 
    generate_verification_token, 
    confirm_verification_token
)
from libs.email import send_email
from flask import render_template, make_response

user_schema = UserSchema()
user_list_schema = ListSchema(many=True)
list_schema = ListSchema(many=True)

class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            password = generate_password_hash(user_json['password'])
            user_json['password'] = password
            user = user_schema.load(user_json)
            token = generate_verification_token(user.email)

            if UserModel.find_by_username(user.username):
                return {"message": gettext("user_username_exists")}, 400

            if UserModel.find_by_email(user.email):
                return {"message": gettext("user_email_exists")}, 400

            verification_email = "http://127.0.0.1:5000/confirm/"+token
            html = render_template_string("<p>Welcome! Thanks for \
            signing up. Please follow this link to activate your \
            account:</p> <p><a href='{{ verification_email }}'>{{ \
            verification_email }}</a></p> <br> <p>Thanks!</p>",
            verification_email=verification_email)
            subject = "Please Verify your email"
            send_email(user.email, subject, html)

            user.save_to_db()
            return {"message": gettext("user_registered")}, 201

        except Exception as e:
            print(e)
            return {"message": gettext("user_invalid_input")}, 402

class UserConfirm(Resource):
    def get( cls, token: str ) -> Response:
        try:
           email = confirm_verification_token(token)
        except:
            return {"message": gettext("user_verification_token_invalid")}, 401
        user = UserModel.query.filter_by(email=email).first_or_404()
        if user.isVerified:
            return make_response(render_template('confirmed.html'))
        else:
            user.isVerified = True
            user.save_to_db()
            return make_response(render_template('index.html'))

class ResendConfirmation(Resource):
    def post(cls):
        email_json = request.get_json()
        
        if not UserModel.find_by_email(email_json['email']):
            return {"message": gettext("user_not_existed")}, 400

        token = generate_verification_token(email_json['email'])
        email = confirm_verification_token(token)
        verification_email = "http://127.0.0.1:5000/confirm/"+token
        html = render_template_string("<p>Welcome! Thanks for \
        signing up. Please follow this link to activate your \
        account:</p> <p><a href='{{ verification_email }}'>{{ \
        verification_email }}</a></p> <br> <p>Thanks!</p>",
        verification_email=verification_email)
        subject = "Please Verify your email"
        try:
            send_email(email_json['email'], subject, html)
            return {"message": gettext("resend_email_success")}, 200
        except Exception as e:
            print(e)
            return {"message": gettext("resend_email_fail")}, 500

class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = UserModel.find_by_username(user_json['username'])
     
        if not user:
            return {"message": gettext("user_not_existed")}, 404

        if user and not user.isVerified:
            return {"message": gettext("user_not_confirmed")}, 400

        if user.verify_hash(user_json['password']):
            access_token = create_access_token(user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return (
                    {"access_token": access_token, "refresh_token": refresh_token,
                    "username": user.username, "user_id" : user.id
                    },
                    200,
                )
        return {"message": gettext("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

class LikeList(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls, list_id):
        the_list = ListModel.find_by_id(list_id)
        if not the_list:
            return {"message": gettext("list_not_existed")}, 404
        user_id = get_jwt_identity()
        current_user = UserModel.find_by_id(user_id)
        like = current_user.like_list(list_id)
        if like:
            return {"message": gettext("user_liked").format(user_id)}, 200
        else:
            return {"message": gettext("user_already_liked").format(user_id)}, 400

class LikedList(Resource):
    @classmethod
    @jwt_refresh_token_required
    def get(cls, list_id):
         the_list = ListModel.find_by_id(list_id)
         if not the_list:
            return {"message": gettext("list_not_existed")}, 404
         user_id = get_jwt_identity()
         if ListLikeModel.query.filter_by(user_id=user_id, list_id=list_id).first():
            return True
         else:
            return False

class UnlikeList(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls, list_id):
        the_list = ListModel.find_by_id(list_id)
        if not the_list:
            return {"message": gettext("list_not_existed")}, 404
        user_id = get_jwt_identity()
        current_user = UserModel.find_by_id(user_id)
        like = current_user.unlike_list(list_id)
        if like:
            return {"message": gettext("user_unliked").format(user_id)}, 200 
        else:
            return {"message": gettext("user_not_liked").format(user_id)}, 200

class SignUpEvent(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls, event_id):
        event = EventModel.find_by_id(event_id)
        if not event:
            return {"message": gettext("event_not_exist")}, 404
        user_id = get_jwt_identity()
        current_user = UserModel.find_by_id(user_id)
        signup = current_user.sign_up_event(event_id)
        if signup:
            return {"message": gettext("user_signed_up").format(user_id)}, 200
        else:
            return {"message": gettext("user_already_signed_up").format(user_id)}, 400

class UndoSignUpEvent(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls, event_id):
        event = EventModel.find_by_id(event_id)
        user_id = get_jwt_identity()
        if not event:
            return {"message": gettext("event_not_exist")}, 404
        elif event.user_id == user_id:
            return {"message": gettext("organizer_undo")}, 400
        current_user = UserModel.find_by_id(user_id)
        undo = current_user.undo_sign_up(event_id)
        if undo:
            return {"message": gettext("user_undo_sign_up").format(user_id)}, 200
        else:
            return {"message": gettext("user_not_signed_up").format(user_id)}, 400

class ListByMember(Resource):
    @classmethod
    @jwt_refresh_token_required
    def get(cls):
        user_id = get_jwt_identity()
        user = UserModel.query.filter_by(id=user_id).first()
        return {"lists": user_list_schema.dump(user.lists)}, 200

class GetUserBio(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_existed")}, 404
        else:
            return {"bio": user_schema.dump(user)["bio"]}, 200

class UpdateUserBio(Resource):
    @classmethod
    @jwt_required
    def put(cls, user_id):
        user = UserModel.find_by_id(user_id) 
        if not user:
            return {"message": gettext("user_not_existed")}, 404
        user.bio = request.get_json()["bio"]
        user.save_to_db()
        return {"bio": user_schema.dump(user)["bio"]}, 200

class GetUserProfile(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_existed")}, 404
        return user_schema.dump(user), 200

class GetLikedList(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_existed")}, 404
        likes = ListLikeModel.query.filter_by(user_id=user_id).all()
        lists = []
        for like in likes:
            list_id = like.list_id
            list1 = ListModel.find_by_id(list_id)
            lists.append(list1)
        return list_schema.dump(lists), 200




from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from models.user import UserModel
from models.friendrequest import FriendRequestModel
from schemas.friendrequest import FriendRequestSchema
from flask_restful import Resource
from libs.strings import gettext

friendrequest_schema = FriendRequestSchema(many=True)

class SendRequest(Resource):
    @classmethod
    @jwt_required
    def post(cls, to_user_id):
        if not UserModel.find_by_id(to_user_id):
            return {"message": gettext("user_not_existed")}, 404
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        if to_user_id == user_id:
            return {"message": gettext("user_request_to_itself").format(user_id)}, 400
        if user.send_request(to_user_id):
            return {"message": gettext("user_request_success").format(user_id)}, 200
        else:
            return {"message": gettext("user_request_existed").format(user_id)}, 400

class HasSentRequest(Resource):
    @classmethod
    @jwt_required
    def get(cls, to_user_id):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        return user.has_sent_request(to_user_id)

class AcceptRequest(Resource):
    @classmethod
    @jwt_required
    def post(cls, from_user_id):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        fq = FriendRequestModel.query.filter_by(from_user_id=from_user_id, to_user_id=user_id).first()
        if not fq:
            return {"message": gettext("user_request_not_existed").format(user_id)}, 400
        elif fq.status == "accepted":
            return {"message": gettext("user_request_accepted").format(user_id)}, 400
        else:
            user.accept_request(from_user_id)
            return {"message": gettext("user_accept_request_success").format(user_id)}, 200

class PendingRequests(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        requests = FriendRequestModel.query.filter_by(to_user_id=user_id, status="pending").all()
        return friendrequest_schema.dump(requests), 200
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from models.user import UserModel
from models.friendship import FriendShipModel
from schemas.friendship import FriendShipSchema
from flask_restful import Resource
from libs.strings import gettext

friend_list_schema = FriendShipSchema(many=True)

class FriendLists(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        friends = FriendShipModel.query.filter((FriendShipModel.user1_id == user_id) | (FriendShipModel.user2_id == user_id)).all()
        return friend_list_schema.dump(friends), 200
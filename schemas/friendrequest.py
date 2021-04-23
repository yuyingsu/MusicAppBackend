from ma import ma
from models.friendrequest import FriendRequestModel

class FriendRequestSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = FriendRequestModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
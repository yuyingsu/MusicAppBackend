from ma import ma
from models.friendship import FriendShipModel

class FriendShipSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = FriendShipModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
from ma import ma
from models.address import AddressModel
from schemas.event import EventSchema
from marshmallow_sqlalchemy import ModelSchema

class AddressSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = AddressModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
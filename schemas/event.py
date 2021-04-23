from ma import ma
from models.user import EventModel
from marshmallow_sqlalchemy import ModelSchema

class EventSchema(ma.SQLAlchemyAutoSchema):

    users = ma.Nested('UserSchema', many=True)
  
    class Meta:
        model = EventModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
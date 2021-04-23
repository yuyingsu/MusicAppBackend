from ma import ma
from models.list import ListModel
from marshmallow_sqlalchemy import ModelSchema

class ListSchema(ma.SQLAlchemyAutoSchema):
    
    songs = ma.Nested('SongSchema', many=True)

    class Meta:
        model = ListModel
        dump_only = ("id",)
        include_fk = True
        load_instance = True
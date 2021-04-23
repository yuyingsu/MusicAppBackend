from ma import ma
from models.song import SongModel

class SongSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = SongModel
        dump_only = ("id",)
        load_instance = True

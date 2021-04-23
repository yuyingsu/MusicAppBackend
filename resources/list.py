from libs.strings import gettext
from models.list import ListModel
from models.user import UserModel
from models.listlike import ListLikeModel
from schemas.list import ListSchema
from schemas.song import SongSchema
from schemas.user import UserSchema
from flask_restful import Resource
from libs.song_analyzer import playlist_score, compare_playlist
from app import pagination
from flask import request
from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
import random

list_schema = ListSchema()
list_list_schema = ListSchema(many=True)

song_schema = SongSchema()
song_list_schema = SongSchema(many=True)

user_schema = UserSchema(many=True)

class List(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        list_json = request.get_json()
        list = list_schema.load(list_json)
        try:
            list.save_to_db()
            return {"message": gettext("list_song_inserting_success")}, 200
        except:
            return {"message": gettext("list_error_inserting")}, 500
    
class ListsList(Resource):
    @classmethod
    def get(cls,page):
        searchTerm = request.args['term']
        if not searchTerm:
            res = [ list_schema.dump(item) for item in ListModel.query.paginate(page=page, per_page=6).items]
            return jsonify({'lists':res, 'count':ListModel.query.filter().count()})
        else:
            look_for = '%{0}%'.format(searchTerm)
            res = [ list_schema.dump(item) for item in ListModel.query.filter(ListModel.title.like(look_for)).paginate(page=page, per_page=6).items]
            return jsonify({'lists':res, 'count':ListModel.query.filter(ListModel.title.like(look_for)).count()})

class ManageList(Resource):
    @classmethod
    def get(cls, list_id):
        list = ListModel.find_by_id(list_id)
        if not list:
            return {"message": gettext("list_not_existed")}, 404
        return list_schema.dump(list), 200

    @classmethod
    @jwt_required
    def delete(cls, list_id):
        user_id = get_jwt_identity()
        the_list = ListModel.find_by_id(list_id)
        if not the_list:
            return {"message": gettext("list_not_existed")}, 404
        ListModel.find_by_id(list_id).delete_from_db()
        like = ListLikeModel.query.filter_by(list_id=list_id, user_id=user_id).first()
        if like:
            like.delete_from_db()
        return {"message": gettext("list_deleted")}, 200

class GetUserLike(Resource):
    @classmethod
    def get(cls, list_id):
        the_list = ListModel.find_by_id(list_id)
        if not the_list:
            return {"message": gettext("list_not_existed")}, 404
        likes = ListLikeModel.query.filter_by(list_id=list_id).all()
        users = []
        for like in likes:
            user_id = like.user_id
            user = UserModel.find_by_id(user_id)
            users.append(user)
        return user_schema.dump(users), 200

class Recommendate(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_existed")}, 404
        likes = ListLikeModel.query.filter_by(user_id=user_id)
        if likes.count()==0:
            return {"message": gettext("user_no_liked_list")}, 400
        idx = random.randint(1, likes.count())
        randomLike = likes[idx-1].list_id
        list2 = ListModel.query.filter_by(id=randomLike).first()
        alllists = ListModel.find_all()
        candidates = {}
        for list1 in alllists:
            if not ListLikeModel.query.filter_by(user_id=user_id, list_id=list1.id).first() and not list1.user_id==user_id:
                score1 = playlist_score(song_list_schema.dump(list1.songs))
                score2 = playlist_score(song_list_schema.dump(list2.songs))
                res = compare_playlist(score1,score2)
                candidates[list1]=res
        sortedItems = {k: v for k, v in sorted(candidates.items(), key=lambda item: item[1])}
        res=[]
        for num in range(min(2, len(sortedItems))):
            res.append(list(sortedItems.keys())[num])
        return list_list_schema.dump(res),200


        
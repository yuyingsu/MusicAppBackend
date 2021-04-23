from libs.strings import gettext
from models.user import UserModel, EventModel
from models.address import AddressModel
from schemas.address import AddressSchema
from schemas.event import EventSchema
from schemas.user import UserSchema
from flask_restful import Resource
from flask import jsonify
from flask import request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    jwt_refresh_token_required
)
import datetime

event_schema = EventSchema()
address_schema = AddressSchema()
event_list_schema = EventSchema(many=True)
event_user_schema = UserSchema(many=True)

class Event(Resource):

    @classmethod
    @jwt_required
    def post(cls):

        event_json = request.get_json()
        
        description = event_json["description"]
        headline = event_json["headline"] 
        date = event_json["date"]
    
        streetName = event_json["streetName"]
        city = event_json["city"]
        state = event_json["state"]
        zip = event_json["zip"]

        address = AddressModel.query.filter_by(streetName=streetName, city=city, state=state, zip=zip).first()

        if address:
            event_json['address_id'] = int(address.id)
        else:
            data = {}
            data['streetName'] = streetName
            data['city'] = city
            data['state'] = state
            data['zip'] = zip
            address = address_schema.load(data)
            address.save_to_db()
            event_json['address_id'] = address.id

        address_id = event_json['address_id']

        if EventModel.query.filter_by(description=description, headline=headline, address_id=address_id,
        date=date).first():
            return {"message": gettext("event_exists")}, 400

        del event_json['streetName']
        del event_json['city']
        del event_json['state']
        del event_json['zip']

        print(event_json)

        event = event_schema.load(event_json)

        try:   
            user = UserModel.find_by_id(event_json["user_id"])
            event.users.append(user)
            event.save_to_db()
        except:
            return {"message": gettext("event_error_inserting")}, 500

        return event_schema.dump(event), 201

class EventsList(Resource):
    @classmethod
    def get(cls,page):
        searchTerm = request.args['term']
        if not searchTerm:
            res = [ event_schema.dump(item) for item in EventModel.query.paginate(page=page, per_page=6).items]
            return jsonify({'events':res, 'count':EventModel.query.filter().count()})
        else:
            look_for = '%{0}%'.format(searchTerm)
            res = [ event_schema.dump(item) for item in EventModel.query.filter(EventModel.headline.like(look_for)).paginate(page=page, per_page=6).items]
            return jsonify({'events':res, 'count':EventModel.query.filter(EventModel.headline.like(look_for)).count()})

class ParticipatorsEvent(Resource):
    @classmethod
    def get(cls, event_id):
        event = EventModel.query.filter_by(id=event_id).first()
        return {"participators": event_user_schema.dump(event.users)}, 200

class GetEvent(Resource):
    @classmethod
    def get(cls, id):
        event = EventModel.find_by_id(id)
        if not event:
             return {"message": gettext("event_not_exist")}, 404
        address_id = EventModel.find_by_id(id).address_id
        return {"event": event_schema.dump(EventModel.find_by_id(id)), 
        "address": address_schema.dump(AddressModel.find_by_id(address_id))}, 200

class RecommendateEvents(Resource):
    @classmethod
    def get(cls,user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_existed")}, 404
        address_id = user.address_id
        zip = AddressModel.find_by_id(address_id).zip
        addresses = AddressModel.query.filter_by(zip=zip)
        events = []
        for address in addresses:
            event = EventModel.query.filter_by(address_id=address.id).first()
            if event and event.date>datetime.datetime.now() and event.user_id!=user.id:
                events.append(event)
        return event_list_schema.dump(events), 200

class GetEventByUser(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_existed")}, 404
        candidates = []
        events = EventModel.find_all()
        for event in events:
            users = event.users
            for user in users:
                if user.id == user_id:
                    candidates.append(event)
                    continue
        return event_list_schema.dump(candidates), 200

class IsAttended(Resource):
    @classmethod
    @jwt_refresh_token_required
    def get(cls, event_id):
        event = EventModel.find_by_id(event_id)
        if not event:
            return {"message": gettext("event_not_exist")}, 404
        user_id = get_jwt_identity()
        for user in event.users:
            if user.id == user_id:
                return True
        return False
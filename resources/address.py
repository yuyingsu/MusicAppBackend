from libs.strings import gettext
from models.address import AddressModel
from schemas.address import AddressSchema
from flask_restful import Resource
from flask import request

address_schema = AddressSchema()

class Address(Resource):

    @classmethod
    def post(cls):
        address_json = request.get_json()

        streetName = address_json["streetName"]
        city = address_json["city"]
        state = address_json["state"] 
        zip = address_json["zip"]

        address = AddressModel.query.filter_by(streetName=streetName, city=city, state=state, zip=zip).first()
        
        if address:
            return address_schema.dump(address), 200

        address = address_schema.load(address_json)

        try:
            address.save_to_db()
        except:
            return {"message": gettext("address_error_inserting")}, 500

        return address_schema.dump(address), 201

class GetAddress(Resource):
    @classmethod
    def get(cls, id):
        if not AddressModel.find_by_id(id):
            return {"message": gettext("address_not_existed")}, 404
        return address_schema.dump(AddressModel.find_by_id(id)), 200

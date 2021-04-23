from db import db

class AddressModel(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True)
    streetName = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    zip = db.Column(db.Integer, nullable=False)
    
    @classmethod
    def find_by_id(cls, _id: int) -> "AddressModel":
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
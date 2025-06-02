from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db: SQLAlchemy = SQLAlchemy()


class Client(db.Model):  # type: ignore[name-defined]
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    credit_card = db.Column(db.String, nullable=False)
    car_number = db.Column(db.String, nullable=False, unique=True)

    parkings = db.relationship(
        "ClientParking", back_populates="client", cascade="all, delete-orphan"
    )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "credit_card": self.credit_card,
            "car_number": self.car_number,
        }

    def __repr__(self):
        return f"<Client id={self.id} name={self.name} {self.surname}>"


class Parking(db.Model):
    __tablename__ = "parking"

    id = db.Column(db.Integer, primary_key=True, index=True)
    address = db.Column(db.String, nullable=False)
    opened = db.Column(db.Boolean, nullable=False, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    clients = db.relationship(
        "ClientParking", back_populates="parking", cascade="all, delete-orphan"
    )

    def to_json(self):
        return {
            "id": self.id,
            "address": self.address,
            "opened": self.opened,
            "count_places": self.count_places,
            "count_available_places": self.count_available_places,
        }

    def __repr__(self):
        return f"<Parking id={self.id} address={self.address} opened={self.opened}>"


class ClientParking(db.Model):
    __tablename__ = "client_parking"

    id = db.Column(db.Integer, primary_key=True, index=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("client.id"), nullable=False, index=True
    )
    parking_id = db.Column(
        db.Integer, db.ForeignKey("parking.id"), nullable=False, index=True
    )
    time_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_out = db.Column(db.DateTime, nullable=True)

    client = db.relationship("Client", back_populates="parkings")
    parking = db.relationship("Parking", back_populates="clients")

    __table_args__ = (
        UniqueConstraint(
            "client_id", "parking_id", "time_out", name="unique_parking_session"
        ),
    )

    def to_json(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "parking_id": self.parking_id,
            "time_in": self.time_in.isoformat(),
            "time_out": self.time_out.isoformat() if self.time_out else None,
        }

    def __repr__(self):
        return f"<ClientParking id={self.id} client={self.client_id} parking={self.parking_id}>"

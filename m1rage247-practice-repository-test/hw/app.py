from datetime import datetime

from flask import Flask, jsonify, request
from models import Client, ClientParking, Parking, db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite_python.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Создаем таблицы при запуске приложения
    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/clients", methods=["POST"])
    def create_user():
        """POST /clients — создать нового клиента."""
        data = request.get_json()
        name = str(data.get("name")) if data.get("name") is not None else None
        email = str(data.get("email")) if data.get("email") is not None else None
        surname = str(data.get("surname")) if data.get("surname") is not None else None
        credit_card = (
            str(data.get("credit_card"))
            if data.get("credit_card") is not None
            else None
        )
        car_number = (
            str(data.get("car_number")) if data.get("car_number") is not None else None
        )

        new_client = Client(
            name=name,
            surname=surname,
            email=email,
            credit_card=credit_card,
            car_number=car_number,
        )

        db.session.add(new_client)
        db.session.commit()

        return jsonify(new_client.to_json()), 201

    @app.route("/clients", methods=["GET"])
    def get_clients():
        """GET /clients — список всех клиентов."""
        clents = db.session.query(Client).all()
        clents_list = [u.to_json() for u in clents]
        return jsonify(clents_list), 200

    @app.route("/clients/<client_id>", methods=["GET"])
    def get_client_by_id(client_id):
        """GET /clients/<client_id> — информация клиента по ID."""
        user = db.session.query(Client).get(client_id)
        if not user:
            return jsonify({"error": "Client not found"}), 404
        return jsonify(user.to_json()), 200

    @app.route("/parkings", methods=["POST"])
    def create_parking():
        """POST /parkings — создать новую парковочную зону."""
        data = request.get_json()
        address = str(data.get("address")) if data.get("address") is not None else None
        opened = bool(data.get("opened")) if data.get("opened") is not None else None
        count_places = (
            int(data.get("count_places"))
            if data.get("count_places") is not None
            else None
        )
        count_available_places = (
            int(data.get("count_available_places"))
            if data.get("count_available_places") is not None
            else None
        )

        new_parking = Parking(
            address=address,
            opened=opened,
            count_places=count_places,
            count_available_places=count_available_places,
        )

        db.session.add(new_parking)
        db.session.commit()

        return jsonify(new_parking.to_json()), 201

    @app.route("/client_parkings", methods=["POST"])
    def enter_parking():
        """POST /client_parkings — заезд на парковку."""
        data = request.get_json()
        client_id = (
            int(data.get("client_id")) if data.get("client_id") is not None else None
        )
        parking_id = (
            int(data.get("parking_id")) if data.get("parking_id") is not None else None
        )

        parking = db.session.query(Parking).get(parking_id)
        if not parking or not parking.opened:
            return jsonify({"error": "Парковка не найдена или закрыта"}), 400
        if parking.count_available_places <= 0:
            return jsonify({"error": "Нет свободных мест"}), 400

        # Проверка на существование записи
        existing = (
            db.session.query(ClientParking)
            .filter_by(client_id=client_id, parking_id=parking_id)
            .first()
        )
        if existing:
            return jsonify({"error": "Клиент уже находится на парковке"}), 400

        # Добавляем заезд
        client_parking = ClientParking(
            client_id=client_id,
            parking_id=parking_id,
            time_in=datetime.utcnow(),
            time_out=None,
        )
        parking.count_available_places -= 1
        db.session.add(client_parking)
        db.session.commit()

        return "", 201

    @app.route("/client_parkings", methods=["DELETE"])
    def leave_parking():
        """DELETE /client_parkings — выезд с парковки."""
        data = request.get_json()
        client_id = (
            int(data.get("client_id")) if data.get("client_id") is not None else None
        )
        parking_id = (
            int(data.get("parking_id")) if data.get("parking_id") is not None else None
        )

        record = (
            db.session.query(ClientParking)
            .filter_by(client_id=client_id, parking_id=parking_id, time_out=None)
            .first()
        )
        if not record:
            return jsonify({"error": "Клиент не найден на парковке"}), 400
        elif (
            db.session.query(Client).filter_by(id=client_id).first().credit_card is None
        ):
            return (
                jsonify({"error": "Проблема оплаты (У клиента нет кредитной карты)"}),
                400,
            )

        record.time_out = datetime.utcnow()

        parking = db.session.query(Parking).get(parking_id)
        parking.count_available_places += 1

        db.session.commit()

        return "", 204

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

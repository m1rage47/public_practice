import pytest
from app import create_app
from models import Client, Parking
from models import db as _db  # Убедитесь, что все модели импортированы


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///:memory:"  # Используем in-memory БД для тестов
    )

    with _app.app_context():
        # Регистрируем модели
        _db.create_all()

        # Добавляем тестовые данные
        client = Client(
            id=1,
            name="Antonio",
            surname="Margareitti",
            email="AntonioMargareitti@blablabla.com",
            credit_card="1234567890123456",
            car_number="AA1234BB",
        )
        parking = Parking(
            id=1,
            address="Moscow, Red Square",
            opened=True,
            count_places=100,
            count_available_places=50,
        )
        # client_parking = ClientParking(
        #     id=1,
        #     client_id=1,
        #     parking_id=1,
        #     time_in=datetime.now(timezone.utc)  # Используем timezone-aware datetime
        # )

        _db.session.add(client)
        _db.session.add(parking)
        # _db.session.add(client_parking)
        _db.session.commit()

        yield _app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db

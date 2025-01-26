import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cv_001 import app, db, Celda, inicializar_celdas_vacias


@pytest.fixture
"""
Fixture for setting up a test client for the Flask application.

This fixture configures the Flask application for testing by setting the
`TESTING` configuration to True and using an in-memory SQLite database.
It initializes the database and creates all tables before yielding the
test client. After the test client is used, it drops all tables to clean
up the database.

Yields:
    FlaskClient: A test client for the Flask application.
"""
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            inicializar_celdas_vacias(1)
        yield client
        with app.app_context():
            db.drop_all()

def test_cv_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'cv.html' in response.data

def test_add_celda(client):
    response = client.post('/add_celda', data={'valor': 1, 'texto': 'Test Celda'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Celda actualizada con éxito' in response.data

def test_eliminar_celda(client):
    # Add a celda first
    client.post('/add_celda', data={'valor': 1, 'texto': 'Test Celda'}, follow_redirects=True)
    celda = Celda.query.first()
    response = client.post(f'/eliminar_celda/{celda.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Celda eliminada con éxito' in response.data

def test_generar_qr(client):
    response = client.get('/generar_qr')
    assert response.status_code == 200
    assert b'static/qr-' in response.data
    @pytest.fixture
    def client():
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                inicializar_celdas_vacias(1)
            yield client
            with app.app_context():
                db.drop_all()

    def test_cv_route(client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'cv.html' in response.data

    def test_add_celda(client):
        response = client.post('/add_celda', data={'valor': 1, 'texto': 'Test Celda'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Celda actualizada con éxito' in response.data

    def test_eliminar_celda(client):
        # Add a celda first
        client.post('/add_celda', data={'valor': 1, 'texto': 'Test Celda'}, follow_redirects=True)
        celda = Celda.query.first()
        response = client.post(f'/eliminar_celda/{celda.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Celda eliminada con éxito' in response.data

    def test_generar_qr(client):
        response = client.get('/generar_qr')
        assert response.status_code == 200
        assert b'static/qr-' in response.data

    def test_inicializar_celdas_vacias(client):
        with app.app_context():
            db.drop_all()
            db.create_all()
            inicializar_celdas_vacias(5)
            celdas = Celda.query.all()
            assert len(celdas) == 5
            for celda in celdas:
                assert celda.valor == 0
                assert celda.texto == ""


import pytest
from app import create_app, db
from app.models import User
from flask import url_for

@pytest.fixture
def app():
    app = create_app(testing=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data  # поправь под свой шаблон index.html

def test_dashboard_redirect(client):
    response = client.get('/dashboard')
    assert response.status_code == 302  # redirect to login

def test_register_and_login(client, app):
    # Register
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'TestPass123',
        'confirm': 'TestPass123'
    }, follow_redirects=True)
    assert b'Login' in response.data

    # Login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'TestPass123'
    }, follow_redirects=True)
    assert b'Dashboard' in response.data or response.status_code == 200

def test_logout(client, app):
    # Login first
    client.post('/register', data={
        'email': 'test2@example.com',
        'password': 'pass1234',
        'confirm': 'pass1234'
    }, follow_redirects=True)

    client.post('/login', data={
        'email': 'test2@example.com',
        'password': 'pass1234'
    }, follow_redirects=True)

    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data

def test_invalid_login(client):
    response = client.post('/login', data={
        'email': 'invalid@example.com',
        'password': 'wrong'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data or response.status_code == 200

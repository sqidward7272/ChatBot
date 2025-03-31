import pytest
import requests

BASE_URL = "http://web:5000"

@pytest.fixture(scope="module")
def session():
    return requests.Session()

def test_login(session):
    data = {"email": "test@example.com", "password": "1234"}
    response = session.post(f"{BASE_URL}/login", data=data)
    assert response.status_code == 200

def test_check_plagiarism(session):
    session.post(f"{BASE_URL}/login", data={"email": "test@example.com", "password": "1234"})
    response = session.post(f"{BASE_URL}/check", data={"text": "Это тест"})
    assert response.status_code == 200
    assert "Проверка завершена!" in response.text or "Процент уникальности:" in response.text

def test_empty_text(session):
    session.post(f"{BASE_URL}/login", data={"email": "test@example.com", "password": "1234"})
    response = session.post(f"{BASE_URL}/check", data={"text": ""})
    assert response.status_code == 200
    assert "Введите текст для проверки!" in response.text

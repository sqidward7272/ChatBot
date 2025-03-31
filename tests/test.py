import pytest
import requests

BASE_URL = "http://web:5000"

@pytest.fixture(scope="module")
def session():
    s = requests.Session()

    # Пробуем зарегистрировать (вдруг юзера ещё нет)
    s.post(f"{BASE_URL}/register", data={
        "email": "user@example.com",
        "password": "testpass"
    })

    login_data = {"email": "user@example.com", "password": "testpass"}
    r = s.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    assert r.status_code == 200
    print("✅ Login OK")
    return s

def test_check_valid_text(session):
    response = session.post(f"{BASE_URL}/check", data={"text": "Тестовый текст для анализа"}, allow_redirects=True)
    assert response.status_code == 200
    assert "Проверка завершена!" in response.text
    print("✅ Проверка валидного текста — OK")

def test_check_empty_text(session):
    response = session.post(f"{BASE_URL}/check", data={"text": ""}, allow_redirects=True)
    assert response.status_code == 200
    assert "Введите текст для проверки!" in response.text
    print("✅ Проверка пустого текста — OK")

def test_check_unauthorized():
    response = requests.post(f"{BASE_URL}/check", data={"text": "Незалогиненный запрос"}, allow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.text.lower()
    print("✅ Защита от незалогиненного доступа — OK") 
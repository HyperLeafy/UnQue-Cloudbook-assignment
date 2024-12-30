import pytest
from fastapi.testclient import TestClient
from app.main_app import app
from app.database import session_local, base, db_engine

# Initialize TestClient
client = TestClient(app)

# Fixture to reset the database before each test
@pytest.fixture(autouse=True)
def reset_database():
    base.metadata.drop_all(bind=db_engine)
    base.metadata.create_all(bind=db_engine)
    yield

# Test user registration
def test_register_users():
    student_data = {"user_name": "studentA1", "passwd": "password123", "desigenate": "STUDENT"}
    professor_data = {"user_name": "professorP1", "passwd": "password123", "desigenate": "PROFESSOR"}

    # Register a student
    response = client.post("/auth/register", json=student_data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["user_name"] == "studentA1"
    assert response.json()["desigenate"] == "STUDENT"

    # Register a professor
    response = client.post("/auth/register", json=professor_data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["user_name"] == "professorP1"
    assert response.json()["desigenate"] == "PROFESSOR"

# Test user login
def test_login_users():
    # Register users first
    test_register_users()

    # Log in users
    student_login = client.post("/auth/login", json={"user_name": "studentA1", "passwd": "password123"})
    professor_login = client.post("/auth/login", json={"user_name": "professorP1", "passwd": "password123"})

    assert student_login.status_code == 200
    assert "access_token" in student_login.json()

    assert professor_login.status_code == 200
    assert "access_token" in professor_login.json()

# Test professor availability
def test_set_professor_availability():
    # Log in professor
    test_login_users()
    professor_login = client.post("/auth/login", json={"user_name": "professorP1", "passwd": "password123"})
    professor_token = professor_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {professor_token}"}
    availability_data = ["9:00 AM", "10:00 AM", "12:00 AM"]

    response = client.post("/professor/availability", json=availability_data, headers=headers)
    assert response.status_code == 200

# Test student views availability
def test_view_availability():
    test_set_professor_availability()

    student_login = client.post("/auth/login", json={"user_name": "studentA1", "passwd": "password123"})
    student_token = student_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {student_token}"}
    response = client.get("/student/availability/2", headers=headers)

    assert response.status_code == 200
    assert "12:00 AM" in response.json()["available_slots"]

# Test student booking an appointment
def test_book_appointment():
    test_view_availability()

    student_login = client.post("/auth/login", json={"user_name": "studentA1", "passwd": "password123"})
    student_token = student_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {student_token}"}
    booking_data = {"professor_id": 2, "time_slot": "12:00 AM"}

    response = client.post("/student/appointment", json=booking_data, headers=headers)
    assert response.status_code == 200

# Test appointment validation
def test_validate_appointment():
    test_book_appointment()

    student_login = client.post("/auth/login", json={"user_name": "studentA1", "passwd": "password123"})
    student_token = student_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {student_token}"}
    response = client.get("/student/appointments", headers=headers)

    assert len(response.json()) == 1

# Test professor cancels the appointment
def test_cancel_appointment():
    test_validate_appointment()

    professor_login = client.post("/auth/login", json={"user_name": "professorP1", "passwd": "password123"})
    professor_token = professor_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {professor_token}"}
    response = client.delete("/professor/appointment/1", headers=headers)

    assert response.status_code == 200

# Test student's appointment list after cancellation
def test_validate_empty_appointment():
    test_cancel_appointment()

    student_login = client.post("/auth/login", json={"user_name": "studentA1", "passwd": "password123"})
    student_token = student_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {student_token}"}
    response = client.get("/student/appointment", headers=headers)

    assert response.status_code == 400
    assert response.json() == {"detail": "No appoints have been made!"}

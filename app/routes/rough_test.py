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

# Test for user registration and login
def test_register_and_login():
    # 1. Register users
    student_data = {"user_name": "studentA1", "passwd": "password123", "desigenate": "STUDENT"}
    professor_data = {"user_name": "professorP1", "passwd": "password123", "desigenate": "PROFESSOR"}
    
    # Register a student
    response = client.post("/auth/register", json=student_data)
    assert response.status_code == 200
    assert "id" in response.json()  # Check if 'id' exists in the response
    assert response.json()["user_name"] == "studentA1"
    assert response.json()["desigenate"] == "STUDENT"

    # Register a professor
    response = client.post("/auth/register", json=professor_data)
    assert response.status_code == 200
    assert "id" in response.json()  # Check if 'id' exists in the response
    assert response.json()["user_name"] == "professorP1"
    assert response.json()["desigenate"] == "PROFESSOR"

    # 2. Log in users
    student_login = client.post("/auth/login", json={"user_name": "studentA1", "passwd": "password123"})
    professor_login = client.post("/auth/login", json={"user_name": "professorP1", "passwd": "password123"})

    # Check student login response
    assert student_login.status_code == 200
    assert "access_token" in student_login.json()

    # Check professor login response
    assert professor_login.status_code == 200
    assert "access_token" in professor_login.json()

    # Get tokens
    student_token = student_login.json()["access_token"]
    print(student_token)
    professor_token = professor_login.json()["access_token"]

    # 3. Professor sets availability (Example of a further workflow after login)
    headers = {"Authorization": f"Bearer {professor_token}"}
    availability_data = ["9:00 AM", "10:00 AM","12:00 AM"]
    response = client.post("/professor/availability", json=availability_data, headers=headers)
    assert response.status_code == 200

    # 4. Student views availability
    headers = {"Authorization": f"Bearer {student_token}"}
    response = client.get("/student/availability/2", headers=headers)
    assert response.status_code == 200
    assert "12:00 AM" in response.json()["available_slots"]

    # 5. Student books an appointment
    booking_data = {"professor_id": 2, "time_slot": "12:00 AM"}
    response = client.post("/student/appointment", json=booking_data, headers=headers)
    assert response.status_code == 200

    # 6. Validate appointment is created
    response = client.get("/student/appointments", headers=headers)
    assert len(response.json()) == 1

    # 7. Professor cancels the appointment
    headers = {"Authorization": f"Bearer {professor_token}"}
    response = client.delete("/professor/appointment/1", headers=headers)
    assert response.status_code == 200

    # 8. Validate student's appointment list is empty
    headers = {"Authorization": f"Bearer {student_token}"}
    response = client.get("/student/appointment", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "No appoints have been made!"}

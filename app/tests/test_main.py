import pytest
import time

from fastapi.testclient import TestClient

from main import app

from config import (
  TIME_FRAME_TARIFFS,
  TOTAL_SPOTS
)

client = TestClient(app)

def test_index():
  """Test the index page
  """
  response = client.get("/")
  assert response.status_code == 200
  assert response.json() == {"status": "ok"}

def test_parking_lot_list_cars():
  """Test listing cars
  """
  response = client.get("/list")
  assert response.status_code == 200
  assert response.json() == {
    "status": "success",
    "cars": []
  }

def test_parking_lot_add_car_wrong_tariff():
  """Test adding a car with a wrong tariff
  """
  response = client.get("/add", params={"car": "A1", "tariff": "wrong"})
  assert response.status_code == 400

  response_dict = response.json()
  assert response_dict == {
      "status": "error",
      "description":
      f"Invalid tariff (Available options: {TIME_FRAME_TARIFFS})"
  }

def test_parking_lot_add_car():
  """Test adding a car
  """
  response = client.get("/list")
  assert response.status_code == 200

  response = client.get("/add", params={"car": "B1", "tariff": "hourly"})
  assert response.status_code == 200

  response_dict = response.json()
  response_dict.pop("start", None)
  response_dict.pop("finish", None)
  assert response_dict == {"status": "success", "car": "B1", "tariff": "hourly", "location": 1}
  client.get("/remove", params={"location": 1})


def test_parking_lot_remove_car():
  """Test removing a car
  """
  response = client.get("/add", params={"car": "A2", "tariff": "hourly"})
  location = response.json().get("location")
  response = client.get("/remove", params={"location": location})
  assert response.status_code == 200

  response_dict = response.json()
  response_dict.pop("start", None)
  response_dict.pop("finish", None)
  assert response_dict == {"status": "success", "car": "A2", "tariff": "hourly", "location": 1, "fee": "0.00"}

def test_parking_lot_remove_wrong_car():
  """Test removing a car that is not in the parking lot
  """
  response = client.get("/remove", params={"location": 1})
  assert response.status_code == 404

  response_dict = response.json()
  assert response_dict == {"status": "error", "description": "Vehicle not found in location."}

def test_full_parking_lot_add_car():
  """Test adding a car to a full parking lot
  """
  for _ in range(TOTAL_SPOTS):
    response = client.get("/add", params={"car": "C1", "tariff": "hourly"})
    assert response.status_code == 200

  list_response = client.get("/list")
  assert list_response.status_code == 200
  list_response_dict = list_response.json()
  assert len(list_response_dict.get("cars")) == 10

  error_response = client.get("/add", params={"car": "D1", "tariff": "hourly"})
  assert error_response.status_code == 507

  response_dict = error_response.json()
  assert response_dict == {"status": "error", "description": "No free space"}

  for spot in range(1, TOTAL_SPOTS+1):
    response = client.get("/remove", params={"location": spot})
    assert response.status_code == 200

  response = client.get("/list")
  assert response.status_code == 200
  response_dict = response.json()
  assert len(response_dict.get("cars")) == 0


def test_parking_lot_list_cars_default_limit():
  """Test listing cars with default limit
  """
  response = client.get("/list")
  assert response.status_code == 200

  response_dict = response.json()
  assert len(response_dict.get("cars")) == 0

  for _ in range(TOTAL_SPOTS):
    response = client.get("/add", params={"car": "F1", "tariff": "hourly"})
    assert response.status_code == 200

  response = client.get("/list")
  assert response.status_code == 200
  response_dict = response.json()
  assert len(response_dict.get("cars")) == 10

  for spot in range(1, TOTAL_SPOTS+1):
    response = client.get("/remove", params={"location": spot})
    assert response.status_code == 200

  response = client.get("/list")
  assert response.status_code == 200
  response_dict = response.json()
  assert len(response_dict.get("cars")) == 0

def test_parking_lot_list_cars_other_limits():
  """Test listing cars with default limit
  """
  response = client.get("/list")
  assert response.status_code == 200

  response_dict = response.json()
  assert len(response_dict.get("cars")) == 0

  for _ in range(TOTAL_SPOTS):
    response = client.get("/add", params={"car": "F1", "tariff": "hourly"})
    assert response.status_code == 200

  response = client.get("/list?limit=20")
  assert response.status_code == 200
  response_dict = response.json()
  assert len(response_dict.get("cars")) == 20

  response = client.get("/list?limit=5")
  assert response.status_code == 200
  response_dict = response.json()
  assert len(response_dict.get("cars")) == 5

  for spot in range(1, TOTAL_SPOTS):
    response = client.get("/remove", params={"location": spot})
    assert response.status_code == 200

  response = client.get("/list")
  assert response.status_code == 200
  response_dict = response.json()
  assert len(response_dict.get("cars")) == 0
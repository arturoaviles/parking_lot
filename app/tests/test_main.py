from fastapi.testclient import TestClient

from main import app

from config import TOTAL_SPOTS

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

def test_parking_lot_add_car():
  """Test adding a car
  """
  response = client.get("/add", params={"car": "ABC-123", "tariff": "hourly"})
  assert response.status_code == 200

  response_dict = response.json()
  response_dict.pop("start", None)
  assert response_dict == {"status": "success", "car": "ABC-123", "tariff": "hourly", "location": 1}

def test_parking_lot_remove_car():
  """Test removing a car
  """
  response = client.get("/remove", params={"location": 1})
  assert response.status_code == 200

  response_dict = response.json()
  response_dict.pop("start", None)
  response_dict.pop("finish", None)
  assert response_dict == {"status": "success", "car": "ABC-123", "tariff": "hourly", "location": 1, "fee": "0.00"}

def test_parking_lot_remove_wrong_car():
  """Test removing a car that is not in the parking lot
  """
  response = client.get("/remove", params={"location": 2})
  assert response.status_code == 404

  response_dict = response.json()
  assert response_dict == {"status": "error", "description": "Vehicle not found in location."}

def test_full_parking_lot_add_car():
  """Test adding a car to a full parking lot
  """
  for _ in range(TOTAL_SPOTS):
    response = client.get("/add", params={"car": "ABC-123", "tariff": "hourly"})
    assert response.status_code == 200

  response = client.get("/add", params={"car": "ABC-123", "tariff": "hourly"})
  assert response.status_code == 507

  response_dict = response.json()
  assert response_dict == {"status": "error", "description": "No free space"}
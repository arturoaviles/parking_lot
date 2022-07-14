import pytest

from datetime import timedelta
from decimal import Decimal

from config import (
  FREE_MINUTES,
  TIME_FRAME_TARIFFS,
  TOTAL_SPOTS
)

from models.models import (
  Car,
  Ticket,
  ParkingLot,
  ParkingLotFullError,
  ParkingLotLocationEmptyError,
  PaginationStartError,
  PaginationLimitError
)

def test_car_constructor():
  """Test Car constructor."""
  car = Car("A")
  assert car.license_plate == "A"

def test_ticket_constructor():
  """Test Ticket constructor."""
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("B", time_frame, 1, base_tariff_cost)
  assert ticket.car == "B"
  assert ticket.tariff == "hourly"
  assert ticket.location == 1
  assert ticket.fee == ""
  assert ticket.base_tariff_cost == base_tariff_cost

def test_ticket_calculate_fee():
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("C", time_frame, 1, base_tariff_cost)
  ticket.calculate_fee()
  assert ticket.fee == "0.00"

def test_ticket_calculate_fee_hourly_exact_free_minutes():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("D", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(minutes=FREE_MINUTES)
  ticket.calculate_fee(delta)
  assert ticket.fee == "0.00"

def test_ticket_calculate_fee_hourly_free_minutes_plus_1_second():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("E", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(minutes=FREE_MINUTES) + timedelta(seconds=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == TIME_FRAME_TARIFFS.get(time_frame) * 1

def test_ticket_calculate_fee_hourly_free_minutes_plus_1_minute():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("F", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(minutes=FREE_MINUTES) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == TIME_FRAME_TARIFFS.get(time_frame) * 1

def test_ticket_calculate_fee_hourly_1_hour():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("G", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(minutes=60)
  ticket.calculate_fee(delta)
  assert ticket.fee == TIME_FRAME_TARIFFS.get(time_frame) * 1

def test_ticket_calculate_fee_hourly_1_hour_plus_1_minute():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("H", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(minutes=60) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("2"))

def test_ticket_calculate_fee_hourly_2_hours_plus_1_minute():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("I", "hourly", 1, base_tariff_cost)
  delta =  ticket.start + timedelta(minutes=120) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("3"))

def test_ticket_calculate_fee_daily():
  """Test calculate fee for daily ticket."""
  time_frame = "daily"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("J", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(minutes=16)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("1"))

def test_ticket_calculate_fee_daily_24_hours():
  """Test calculate fee for daily ticket."""
  time_frame = "daily"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("K", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(hours=24)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("1"))

def test_ticket_calculate_fee_daily_24_hours_plus_1_minute():
  """Test calculate fee for daily ticket."""
  time_frame = "daily"
  base_tariff_cost = TIME_FRAME_TARIFFS.get(time_frame)
  ticket = Ticket("L", time_frame, 1, base_tariff_cost)
  delta =  ticket.start + timedelta(hours=24) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("2"))

def test_parking_lot_constructor():
  """Test Parking Lot constructor."""
  parking_lot = ParkingLot(10, TIME_FRAME_TARIFFS)
  assert parking_lot.total_spots == 10
  assert parking_lot.occupied_spots == {}

def test_parking_lot_add_car():
  """Test add car to Parking Lot."""
  parking_lot = ParkingLot(10, TIME_FRAME_TARIFFS)
  car = Car("M")
  ticket = parking_lot.add_car(car, "hourly")
  assert ticket.car == "M"
  assert ticket.tariff == "hourly"
  assert ticket.location == 1
  assert parking_lot.occupied_spots == {1: ticket}

def test_full_parking_lot():
  """Test add car to full parking lot."""
  parking_lot = ParkingLot(1, TIME_FRAME_TARIFFS)
  car = Car("N")
  parking_lot.add_car(car, "hourly")
  with pytest.raises(ParkingLotFullError):
    parking_lot.add_car(car, "hourly")

def test_parking_lot_remove_car():
  """Test remove car from Parking Lot."""
  parking_lot = ParkingLot(10, TIME_FRAME_TARIFFS)
  car = Car("O")
  ticket = parking_lot.add_car(car, "hourly")
  assert parking_lot.remove_car(1) == ticket
  assert parking_lot.occupied_spots == {}

def test_parking_lot_remove_wrong_car():
  """Test remove car from wrong location."""
  parking_lot = ParkingLot(10, TIME_FRAME_TARIFFS)
  car = Car("P")
  parking_lot.add_car(car, "hourly")
  with pytest.raises(ParkingLotLocationEmptyError):
    parking_lot.remove_car(2)

def test_parking_lot_list_empty():
  """Test list empty parking lot."""
  parking_lot = ParkingLot(10, TIME_FRAME_TARIFFS)
  assert parking_lot.list_cars() == []

def test_parking_lot_list_cars_pagination():
  """Test list parking lot with pagination."""
  parking_lot = ParkingLot(10, TIME_FRAME_TARIFFS)
  for _ in range(10):
    car = Car("Q")
    parking_lot.add_car(car, "hourly")
  assert len(parking_lot.list_cars()) == 10

def test_parking_lot_list_11_cars_pagination_with_default_limit():
  """Test list parking lot with pagination."""
  parking_lot = ParkingLot(20, TIME_FRAME_TARIFFS)
  for _ in range(11):
    car = Car("R")
    parking_lot.add_car(car, "hourly")
  assert len(parking_lot.list_cars()) == 10

def test_parking_lot_list_cars_pagination_when_removing_one():
  """Test list parking lot with pagination."""
  parking_lot = ParkingLot(20, TIME_FRAME_TARIFFS)
  for _ in range(11):
    car = Car("S")
    parking_lot.add_car(car, "hourly")
  parking_lot.remove_car(2)
  assert len(parking_lot.list_cars()) == 9
  assert len(parking_lot.list_cars(start=11)) == 1

def test_parking_lot_list_cars_pagination_limit():
  """Test list parking lot with pagination."""
  parking_lot = ParkingLot(20, TIME_FRAME_TARIFFS)
  for _ in range(11):
    car = Car("T")
    parking_lot.add_car(car, "hourly")
  assert len(parking_lot.list_cars(limit=5)) == 5

def test_parking_lot_list_cars_pagination_start_and_limit():
  """Test list parking lot with pagination."""
  parking_lot = ParkingLot(20, TIME_FRAME_TARIFFS)
  for _ in range(11):
    car = Car("U")
    parking_lot.add_car(car, "hourly")
  assert len(parking_lot.list_cars(start=5, limit=5)) == 5

def test_parking_lot_list_cars_pagination_start_error_not_valid_spots():
  """Test list parking lot with pagination."""
  parking_lot = ParkingLot(TOTAL_SPOTS, TIME_FRAME_TARIFFS)
  for _ in range(11):
    car = Car("W")
    parking_lot.add_car(car, "hourly")
  with pytest.raises(PaginationStartError):
    parking_lot.list_cars(start=0)
    parking_lot.list_cars(start=-1)
    parking_lot.list_cars(start=TOTAL_SPOTS + 1)

def test_parking_lot_list_cars_pagination_limit_error_():
  """Test list parking lot with pagination."""
  parking_lot = ParkingLot(TOTAL_SPOTS, TIME_FRAME_TARIFFS)
  for _ in range(11):
    car = Car("X")
    parking_lot.add_car(car, "hourly")
  with pytest.raises(PaginationLimitError):
    parking_lot.list_cars(limit=-1)
    parking_lot.list_cars(limit=0)
    parking_lot.list_cars(limit=101)



import pytest

from datetime import datetime, timedelta
from decimal import Decimal

from config import (DATE_TIME_FORMAT, FREE_MINUTES, TIME_FRAME_TARIFFS)
from models.models import Car, Ticket, ParkingLot, ParkingLotFullError, ParkingLotLocationEmptyError

def test_car_constructor():
  """Test Car constructor."""
  car = Car("ABC-123")
  assert car.license_plate == "ABC-123"

def test_ticket_constructor():
  """Test Ticket constructor."""
  ticket = Ticket("ABC-123", "hourly", 1)
  assert ticket.car == "ABC-123"
  assert ticket.tariff == "hourly"
  assert ticket.location == 1
  assert ticket.fee == ""

def test_ticket_calculate_fee():
  ticket = Ticket("ABC-123", "hourly", 1)
  ticket.calculate_fee()
  assert ticket.fee == "0.00"

def test_ticket_calculate_fee_hourly_exact_free_minutes():
  """Test calculate fee for hourly ticket."""
  ticket = Ticket("ABC-123", "hourly", 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(minutes=FREE_MINUTES)
  ticket.calculate_fee(delta)
  assert ticket.fee == "0.00"

def test_ticket_calculate_fee_hourly_free_minutes_plus_1_second():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  ticket = Ticket("ABC-123", time_frame, 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(minutes=FREE_MINUTES) + timedelta(seconds=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == TIME_FRAME_TARIFFS.get(time_frame) * 1

def test_ticket_calculate_fee_hourly_free_minutes_plus_1_minute():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  ticket = Ticket("ABC-123", time_frame, 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(minutes=FREE_MINUTES) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == TIME_FRAME_TARIFFS.get(time_frame) * 1

def test_ticket_calculate_fee_hourly_1_hour():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  ticket = Ticket("ABC-123", time_frame, 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(minutes=60)
  ticket.calculate_fee(delta)
  assert ticket.fee == TIME_FRAME_TARIFFS.get(time_frame) * 1

def test_ticket_calculate_fee_hourly_1_hour_plus_1_minute():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  ticket = Ticket("ABC-123", time_frame, 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(minutes=60) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("2"))

def test_ticket_calculate_fee_hourly_2_hours_plus_1_minute():
  """Test calculate fee for hourly ticket."""
  time_frame = "hourly"
  ticket = Ticket("ABC-123", "hourly", 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(minutes=120) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("3"))

def test_ticket_calculate_fee_daily():
  """Test calculate fee for daily ticket."""
  time_frame = "daily"
  ticket = Ticket("ABC-123", time_frame, 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(minutes=16)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("1"))

def test_ticket_calculate_fee_daily_24_hours():
  """Test calculate fee for daily ticket."""
  time_frame = "daily"
  ticket = Ticket("ABC-123", time_frame, 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(hours=24)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("1"))

def test_ticket_calculate_fee_daily_24_hours_plus_1_minute():
  """Test calculate fee for daily ticket."""
  time_frame = "daily"
  ticket = Ticket("ABC-123", time_frame, 1)
  delta =  datetime.strptime(ticket.start, DATE_TIME_FORMAT) + timedelta(hours=24) + timedelta(minutes=1)
  ticket.calculate_fee(delta)
  assert ticket.fee == str(Decimal(TIME_FRAME_TARIFFS.get(time_frame)) * Decimal("2"))

def test_parking_lot_constructor():
  """Test Parking Lot constructor."""
  parking_lot = ParkingLot(10)
  assert parking_lot.total_spots == 10
  assert parking_lot.occupied_spots == {}

def test_parking_lot_add_car():
  """Test add car to Parking Lot."""
  parking_lot = ParkingLot(10)
  car = Car("ABC-123")
  ticket = parking_lot.add_car(car, "hourly")
  assert ticket.car == "ABC-123"
  assert ticket.tariff == "hourly"
  assert ticket.location == 1
  assert parking_lot.occupied_spots == {1: ticket}

def test_full_parking_lot():
  """Test add car to full parking lot."""
  parking_lot = ParkingLot(1)
  car = Car("ABC-123")
  parking_lot.add_car(car, "hourly")
  with pytest.raises(ParkingLotFullError):
    parking_lot.add_car(car, "hourly")

def test_parking_lot_remove_car():
  """Test remove car from Parking Lot."""
  parking_lot = ParkingLot(10)
  car = Car("ABC-123")
  ticket = parking_lot.add_car(car, "hourly")
  assert parking_lot.remove_car(1) == ticket
  assert parking_lot.occupied_spots == {}

def test_parking_lot_remove_wrong_car():
  """Test remove car from wrong location."""
  parking_lot = ParkingLot(10)
  car = Car("ABC-123")
  parking_lot.add_car(car, "hourly")
  with pytest.raises(ParkingLotLocationEmptyError):
    parking_lot.remove_car(2)

def test_parking_lot_list_empty():
  """Test list empty parking lot."""
  parking_lot = ParkingLot(10)
  assert parking_lot.list_cars() == []


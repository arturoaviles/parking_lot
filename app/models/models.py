from datetime import datetime, timedelta
from decimal import Decimal
from math import floor
from typing import Any, Dict, List, Set

from config import (
	DATE_TIME_FORMAT,
	FREE_MINUTES,
	TIME_FRAME_HOURS,
	TIME_FRAME_TARIFFS
)

class ParkingLotFullError(Exception):
	"""Custom error that is raised when the Parking Lot is full"""
	pass

class ParkingLotLocationEmptyError(Exception):
	"""Custom error that is raised when the Parking Lot location is empty"""
	pass

class Ticket:
	def __init__(self, license_plate: str, tariff: str, location: int) -> None:
		"""Ticket constructor

		Args:
			license_plate (str): Car license plate.
			tariff (str): Tariff for the ticket.
			location (int): Parking Lot location.

		Returns:
			None
		"""
		self.car: str = license_plate
		self.tariff: str = tariff
		self.location: int = location
		self.start: str = datetime.now().strftime(DATE_TIME_FORMAT)
		self.finish: str = ""
		self.fee: str = ""

	def _get_total_time(self) -> timedelta:
		"""Get the total time for the ticket

		Returns:
			timedelta: Total time for the ticket.
		"""
		try:
			start = datetime.strptime(self.start, DATE_TIME_FORMAT)
			finish = datetime.strptime(self.finish, DATE_TIME_FORMAT)
		except ValueError as e:
			raise ValueError("Invalid date format") from e
		return finish - start

	def calculate_fee(self, end_datetime: datetime = datetime.now()) -> None:
		"""Calculate the fee for the ticket

		Returns:
			None
		"""
		self.finish = end_datetime.strftime(DATE_TIME_FORMAT)
		delta = self._get_total_time()
		total_minutes = delta / timedelta(minutes=1)

		if total_minutes <= FREE_MINUTES:
			self.fee = "0.00"
			return

		time_frame = TIME_FRAME_HOURS.get(self.tariff)
		tariff = TIME_FRAME_TARIFFS.get(self.tariff)

		total_time = delta / timedelta(hours=time_frame)

		if not total_time.is_integer():
			total_time += 1

		self.fee = str(Decimal(tariff) * Decimal(floor(total_time)))


class Car:
	def __init__(self, license_plate: str) -> None:
		"""Car constructor.

		Args:
			license_plate (str): Car license plate.

		Returns:
			None
		"""
		self.license_plate = license_plate


class ParkingLot:
	def __init__(self, total_spots: int) -> None:
		"""Parking Lot constructor.

		Returns:
			None
		"""
		self.total_spots: int = total_spots
		self.available_spots: Set[int] = set(range(1, self.total_spots+1))
		self.occupied_spots: Dict[int, Ticket] = {}

	def add_car(self, car: Car, tariff: str) -> Ticket:
		"""Add car to the Parking Lot.

		Returns:
			Ticket: Ticket object with the car information.

		Raises:
			ParkingLotFullError: If the Parking Lot is full.
		"""

		try:
			available_spot = self.available_spots.pop()
		except KeyError as e: # Full parking Lot
			raise ParkingLotFullError("No free space") from e

		self.occupied_spots[available_spot] = Ticket(car.license_plate, tariff, available_spot)

		return self.occupied_spots[available_spot]


	def remove_car(self, parking_spot: int) -> Ticket:
		"""Remove car from Parking Lot.

		Returns:
			Ticket: Ticket object with the car information.

		Raises:
			ParkingLotLocationEmptyError: If the Parking Lot location is empty.
		"""
		try:
			ticket = self.occupied_spots.pop(parking_spot)
		except KeyError as e:
			raise ParkingLotLocationEmptyError("The location is empty") from e

		ticket.calculate_fee()

		self.available_spots.add(parking_spot)

		return ticket


	def list_cars(self) -> List[Dict[str, Any]]:
		"""List cars in the Parking Lot.

		Returns:
			List[Dict[str, Any]]: List of cars in the Parking Lot.
		"""
		return [vars(ticket) for ticket in self.occupied_spots.values()]



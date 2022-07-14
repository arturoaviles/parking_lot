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

class PaginationLimitError(Exception):
	"""Custom error that is raised when the Pagination limit is not between 1 and 100"""
	pass

class PaginationStartError(Exception):
	"""Custom error that is raised when the Pagination start is not between 1 and Parking Lot total spots"""
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
		self.occupied_spots: Dict[int, Ticket] = {}

	def add_car(self, car: Car, tariff: str) -> Ticket:
		"""Add car to the Parking Lot.

		Returns:
			Ticket: Ticket object with the car information.

		Raises:
			ParkingLotFullError: If the Parking Lot is full.
		"""
		available_spot = len(self.occupied_spots) + 1
		if available_spot <= self.total_spots:
			self.occupied_spots[available_spot] = Ticket(car.license_plate, tariff, available_spot)
			return self.occupied_spots[available_spot]
		raise ParkingLotFullError("No free space")

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
			raise ParkingLotLocationEmptyError("Vehicle not found in location.") from e

		ticket.calculate_fee()

		return ticket


	def list_cars(self, start: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
		"""List cars in the Parking Lot.

		Args:
			start (int): Start index of cars to list.
			limit (int): Limit of cars to list.

		Returns:
			List[Dict[str, Any]]: List of cars in the Parking Lot.
		"""
		if start <= 0 or start > self.total_spots:
			raise PaginationStartError("Start must be between 1 and %d" % self.total_spots)

		if limit <= 0 or limit > 100:
			raise PaginationLimitError("Limit must be between 1 and 100")

		cars = []

		if len(self.occupied_spots) == 0:
			return cars

		for spot in range(start, start + limit):
			if ticket := self.occupied_spots.get(spot):
				cars.append({
					"license_plate": ticket.car,
					"tariff": ticket.tariff,
					"location": ticket.location,
					"start": ticket.start,
					"finish": ticket.finish,
					"fee": ticket.fee
				})
		return cars



from fastapi import FastAPI
from fastapi.responses import JSONResponse

from models.models import (
	ParkingLot,
	Car,
	ParkingLotFullError,
	ParkingLotLocationEmptyError,
	PaginationLimitError,
	PaginationStartError,
	Configuration
)

from config import (
	TOTAL_SPOTS,
	TIME_FRAME_TARIFFS
)

app = FastAPI()

parking_lot = ParkingLot(TOTAL_SPOTS, TIME_FRAME_TARIFFS)

@app.get("/")
def index() -> JSONResponse:
	""" Returns the index page """
	return JSONResponse(content={"status": "ok"}, status_code=200)

@app.get("/add")
def add_car(car: str, tariff: str):
	"""Add car to the parking lot endpoint handler

	Returns:
		JSONResponse:
				error: JSON with the error message.
				success: JSON with the ticket information.
	"""
	tariff = tariff.lower()
	if tariff not in TIME_FRAME_TARIFFS:
		return JSONResponse(
			content={
				"status": "error",
				"description": f"Invalid tariff (Available options: {TIME_FRAME_TARIFFS})"
			},
			status_code=400
		)

	try:
		ticket = parking_lot.add_car(Car(car), tariff)
	except ParkingLotFullError as e:
		return JSONResponse(
			content={
				"status": "error",
				"description": str(e)
			},
			status_code=507
		)

	return JSONResponse(
		content={
			"status": "success",
			"car": ticket.car,
			"tariff": ticket.tariff,
			"location": ticket.location,
			"start": ticket.start,
			"base_cost": ticket.base_tariff_cost
		},
		status_code=200
	)


@app.get("/remove")
def remove_car(location: int) -> JSONResponse:
	"""Remove car from parking lot endpoint handler.

	Returns:
			JSONResponse:
				error: JSON with the error message.
				success: JSON with the ticket information and its fee.
	"""
	try:
		ticket = parking_lot.remove_car(location)
	except ParkingLotLocationEmptyError as e:
		return JSONResponse(
			content={
				"status": "error",
				"description": str(e)
			},
			status_code=404
		)

	return JSONResponse(
		content={
			"status": "success",
			"start": ticket.start,
			"finish": ticket.finish,
			"location": ticket.location,
			"car": ticket.car,
			"tariff": ticket.tariff,
			"base_cost": ticket.base_tariff_cost,
			"fee": ticket.fee
		},
		status_code=200
	)


@app.get("/list")
def list_parked_cars(start: int = 1, limit: int = 10) -> JSONResponse:
	"""List parked cars endpoint handler

	Returns:
			JSONResponse: JSON with the list of cars in the parking lot.
	"""

	try:
		cars = parking_lot.list_cars(start=start, limit=limit)
	except PaginationLimitError as e:
		return JSONResponse(
			content={
				"status": "error",
				"description": str(e)
			},
			status_code=400
		)
	except PaginationStartError as e:
		return JSONResponse(
			content={
				"status": "error",
				"description": str(e)
			},
			status_code=400
		)

	return JSONResponse(
		content={
			"status": "success",
			"cars": cars
		},
		status_code=200
	)

@app.get("/config")
def get_current_config():
	return JSONResponse(
		content={
			"status": "success",
			"total_spots": parking_lot.total_spots,
			"time_frame_tariffs": parking_lot.time_frame_tariffs
		},
		status_code=200
	)

@app.post("/config")
def config(config: Configuration):
	"""Config endpoint handler

	Returns:
			JSONResponse: JSON with the config file.
	"""
	updated_configuration = parking_lot.update_configuration(config)
	return JSONResponse(
		content={
			"status": "success",
			"config": updated_configuration
		},
		status_code=200
	)


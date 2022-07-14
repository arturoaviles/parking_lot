from fastapi import FastAPI
from fastapi.responses import JSONResponse

from models.models import ParkingLot, Car, ParkingLotFullError, ParkingLotLocationEmptyError

from config import (
	TOTAL_SPOTS,
	TIME_FRAME_TARIFFS
)

app = FastAPI()

parking_lot = ParkingLot(TOTAL_SPOTS)

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
			"start": ticket.start
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
			"fee": ticket.fee,
			"tariff": ticket.tariff
		},
		status_code=200
	)


@app.get("/list")
def list_parked_cars() -> JSONResponse:
	"""List parked cars endpoint handler

	Returns:
			JSONResponse: JSON with the list of cars in the parking lot.
	"""
	return JSONResponse(
		content={
			"status": "success",
			"cars": parking_lot.list_cars()
		},
		status_code=200
	)

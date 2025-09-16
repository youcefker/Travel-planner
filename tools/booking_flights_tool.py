import os
import requests
from dotenv import load_dotenv
from langchain.tools import Tool

load_dotenv()

BOOKING_RAPIDAPI_KEY = os.getenv("BOOKING_RAPIDAPI_KEY")

def search_booking_flights(query: str) -> str:
    """
    Search flights with Booking.com RapidAPI.
    Query format: 'fromId=BOM.AIRPORT toId=DEL.AIRPORT departDate=2023-11-25 returnDate=2023-12-02'
    """
    try:
        # Parse input string into dict
        params = dict(p.split("=") for p in query.split())
        from_id = params.get("fromId")
        to_id = params.get("toId")
        depart_date = params.get("departDate")
        return_date = params.get("returnDate", None)

        url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
        querystring = {
            "fromId": from_id,
            "toId": to_id,
            "departDate": depart_date,
            "stops": "none",
            "pageNo": "1",
            "adults": "1",
            "children": "0,17",
            "sort": "CHEAPEST",
            "cabinClass": "ECONOMY",
            "currency_code": "EUR"
        }
        if return_date:
            querystring["returnDate"] = return_date

        headers = {
            "x-rapidapi-key": BOOKING_RAPIDAPI_KEY,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        data = response.json()

        offers = data.get("data", {}).get("flightOffers", [])
        if not offers:
            return "No flights found."

        # Take top 3 offers
        results = []
        for i, offer in enumerate(offers[:3], 1):
            price = offer["priceBreakdown"]["total"]["units"]
            currency = offer["priceBreakdown"]["total"]["currencyCode"]
            first_segment = offer["segments"][0]
            dep_airport = first_segment["departureAirport"]["cityName"]
            arr_airport = first_segment["arrivalAirport"]["cityName"]
            dep_time = first_segment["departureTime"]
            arr_time = first_segment["arrivalTime"]
            airline = first_segment["legs"][0]["carriersData"][0]["name"]

            results.append(
                f"{i}. {airline}: {dep_airport} → {arr_airport}, "
                f"Depart: {dep_time}, Arrive: {arr_time}, "
                f"Price: {price} {currency}"
            )

        return "\n".join(results)

    except Exception as e:
        return f"Error fetching Booking.com flights: {str(e)}"

booking_flights_tool = Tool(
    name="BookingFlightsTool",
    func=search_booking_flights,
    description=(
        "Search flights via Booking.com API. "
        "Input format: 'fromId=BOM.AIRPORT toId=DEL.AIRPORT departDate=YYYY-MM-DD returnDate=YYYY-MM-DD(optional)'. "
        "Returns top flight offers."
    )
)
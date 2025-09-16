import os
import requests
from dotenv import load_dotenv
from langchain.tools import Tool

load_dotenv()

BOOKING_RAPIDAPI_KEY = os.getenv("BOOKING_RAPIDAPI_KEY")

def search_booking_hotels(query: str) -> str:
    """
    Search hotels with Booking.com RapidAPI.
    Query format:
      'dest_id=-2092174 arrival_date=2023-11-21 departure_date=2023-11-22'
    """
    try:
        # Parse query string into dict
        params = dict(p.split("=", 1) for p in query.split())

        dest_id = params.get("dest_id")
        arrival_date = params.get("arrival_date")
        departure_date = params.get("departure_date")

        url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
        querystring = {
            "dest_id": dest_id,
            "search_type": "CITY",
            "arrival_date": arrival_date,
            "departure_date": departure_date,
            "adults": "1",
            "children_age": "0,17",
            "room_qty": "1",
            "page_number": "1",
            "units": "metric",
            "temperature_unit": "c",
            "languagecode": "en-us",
            "currency_code": "EUR",
            "location": "US"
        }

        headers = {
            "x-rapidapi-key": BOOKING_RAPIDAPI_KEY,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        data = response.json()

        hotels = data.get("data", {}).get("hotels", [])
        if not hotels:
            return "No hotels found."

        results = []
        for i, hotel in enumerate(hotels[:5], 1):  # Limit to top 5
            prop = hotel["property"]
            name = prop["name"]
            score = prop.get("reviewScore", "")
            score_word = prop.get("reviewScoreWord", "")
            price_info = prop.get("priceBreakdown", {}).get("grossPrice", {})
            price = price_info.get("value", "N/A")
            currency = price_info.get("currency", "")
            location = prop.get("wishlistName", "")
            photo = prop.get("photoUrls", [None])[0]

            results.append(
                f"{i}. {name} ({score} {score_word}) - {price} {currency}, "
                f"Area: {location}\nPhoto: {photo}"
            )

        return "\n\n".join(results)

    except Exception as e:
        return f"Error fetching hotels: {str(e)}"

booking_hotels_tool = Tool(
    name="BookingHotelsTool",
    func=search_booking_hotels,
    description=(
        "Search hotels via Booking.com API. "
        "Input format: 'dest_id=-2092174 arrival_date=YYYY-MM-DD departure_date=YYYY-MM-DD'. "
        "Returns top hotel options."
    )
)
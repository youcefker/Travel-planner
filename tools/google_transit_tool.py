import os
import requests
from dotenv import load_dotenv
from langchain.tools import Tool

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_transit_directions(query: str) -> str:
    """
    Get public transport directions between places using Google Maps.
    Query format: 'from=Colosseum Rome to=Vatican Museums Rome'
    """
    try:
        # ✅ Safer parsing
        origin, destination = None, None
        if "from=" in query and " to=" in query:
            origin = query.split("from=")[1].split(" to=")[0].strip()
            destination = query.split(" to=")[1].strip()
        else:
            return "Invalid format. Use: 'from=PLACE1 to=PLACE2'"

        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",
            "transit_mode": "bus|subway|train|tram",
            "alternatives": "true",
            "key": GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        routes = data.get("routes", [])
        if not routes:
            return f"No public transit routes found from {origin} to {destination}."

        results = []
        for i, route in enumerate(routes[:2], 1):  # limit to top 2
            legs = route["legs"][0]
            duration = legs["duration"]["text"]
            steps = []
            for step in legs["steps"]:
                travel_mode = step["travel_mode"]
                if travel_mode == "TRANSIT":
                    transit = step["transit_details"]
                    line = transit["line"].get("short_name") or transit["line"]["name"]
                    vehicle = transit["line"]["vehicle"]["type"]
                    dep_stop = transit["departure_stop"]["name"]
                    arr_stop = transit["arrival_stop"]["name"]
                    steps.append(f"{vehicle} {line}: {dep_stop} → {arr_stop}")
                else:
                    steps.append(step["html_instructions"])

            results.append(
                f"Route {i}: Duration {duration}\n" + "\n".join(steps)
            )

        return "\n\n".join(results)

    except Exception as e:
        return f"Error fetching directions: {str(e)}"

google_transit_tool = Tool(
    name="GoogleTransitTool",
    func=get_transit_directions,
    description=(
        "Get public transport directions between two places. "
        "Input format: 'from=PLACE1 to=PLACE2'. "
        "Returns top transit routes with steps."
    )
)
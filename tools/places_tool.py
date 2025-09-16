# travel_planneer/tools/places_tool.py
import os
import json
import googlemaps
from dotenv import load_dotenv
from langchain.tools import Tool

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def find_place_coords(input_text: str) -> str:
    try:
        result = gmaps.find_place(
            input=input_text,
            input_type="textquery",
            fields=["name", "geometry"]
        )
        candidates = result.get("candidates", [])
        if not candidates:
            return json.dumps({"error": f"No coordinates found for '{input_text}'"})

        place = candidates[0]
        loc = place["geometry"]["location"]

        return json.dumps({
            "name": place["name"],
            "lat": loc["lat"],
            "lon": loc["lng"]
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

# Remove any args_schema to force string input
places_tool = Tool(
    name="PlacesTool",
    func=find_place_coords,
    description="Look up coordinates of a place. Input: place name as string."
)
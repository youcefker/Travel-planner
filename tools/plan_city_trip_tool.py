from langchain.tools import Tool
from chains.plan_city_trip import plan_city_trip

def plan_city_trip_func(input: str) -> str:
    return plan_city_trip(input)

plan_city_trip_tool = Tool(
    name="PlanCityTripTool",
    func=plan_city_trip_func,
    description=(
        "Given a city name, search the web for top attractions, "
        "resolve their coordinates, assign durations, and produce "
        "an itinerary ordered by proximity. "
        "Input: city name (e.g., 'Barcelona'). "
        "Output: JSON itinerary with POIs and schedule."
    )
)
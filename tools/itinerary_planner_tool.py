# travel_planneer/tools/itinerary_planner_tool.py
import math
import json
from typing import List, Dict, Tuple, Optional
from langchain.tools import Tool

# ---------- Helpers ----------
def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Return distance in kilometers between two (lat, lon)."""
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    R = 6371.0
    return 2 * R * math.asin(
        math.sqrt(math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2)
    )

def build_distance_matrix(coords: List[Tuple[float, float]]) -> List[List[float]]:
    n = len(coords)
    mat = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                mat[i][j] = haversine_km(coords[i], coords[j])
    return mat

def nearest_neighbor_order(start_index: int, dist_mat: List[List[float]]) -> List[int]:
    n = len(dist_mat)
    unvisited = set(range(n))
    order = [start_index]
    unvisited.remove(start_index)
    current = start_index
    while unvisited:
        next_node = min(unvisited, key=lambda x: dist_mat[current][x])
        order.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    return order

# ---------- Planner ----------
def plan_visit_order(
    pois: List[Dict],
    start_location: Optional[Dict] = None,
    start_at_first: bool = True
) -> List[Dict]:
    """Order POIs by nearest-neighbor heuristic."""
    if not pois:
        return []

    coords = [(p['lat'], p['lon']) for p in pois]
    dist_mat = build_distance_matrix(coords)

    if start_at_first:
        start_idx = 0
    else:
        if start_location:
            start_coord = (start_location['lat'], start_location['lon'])
            dists = [haversine_km(start_coord, c) for c in coords]
            start_idx = int(min(range(len(dists)), key=lambda i: dists[i]))
        else:
            start_idx = 0

    order_idx = nearest_neighbor_order(start_idx, dist_mat)
    return [pois[i] for i in order_idx]

def split_into_periods(
    ordered_pois: List[Dict],
    visit_start_hour: int = 9,
    visit_end_hour: int = 18,
    days: int = 1
) -> Dict:
    """
    Greedy split POIs into days and periods (morning/afternoon).
    """
    if not ordered_pois:
        return {}

    periods = [
        ("morning", visit_start_hour, (visit_start_hour + visit_end_hour)//2),
        ("afternoon", (visit_start_hour + visit_end_hour)//2, visit_end_hour),
    ]

    schedule = {f"day_{d+1}": {} for d in range(days)}

    poi_idx = 0
    n = len(ordered_pois)

    for d in range(days):
        day_key = f"day_{d+1}"
        for period_name, p_start, p_end in periods:
            schedule[day_key][period_name] = []
            remaining_minutes = (p_end - p_start) * 60

            while poi_idx < n and remaining_minutes > 0:
                poi = ordered_pois[poi_idx]
                dur = int(poi.get("duration_min", 60))
                if dur <= remaining_minutes:
                    schedule[day_key][period_name].append(poi)
                    remaining_minutes -= dur
                    poi_idx += 1
                else:
                    break

    if poi_idx < n:
        schedule[f"day_{days}"]["afternoon"].extend(ordered_pois[poi_idx:])

    return schedule

# ---------- Tool Function ----------
def plan_itinerary_tool_input(input_str: str) -> str:
    """
    Expects a JSON string with POIs and parameters.
    Example input:
    {
      "pois": [
        {"name": "Colosseum", "lat": 41.8902, "lon": 12.4922, "duration_min": 60},
        {"name": "Pantheon", "lat": 41.8986, "lon": 12.4768, "duration_min": 45}
      ],
      "days": 1,
      "visit_start_hour": 9,
      "visit_end_hour": 18
    }
    """
    try:
        payload = json.loads(input_str)
        pois = payload.get("pois", [])
        days = payload.get("days", 1)
        visit_start_hour = payload.get("visit_start_hour", 9)
        visit_end_hour = payload.get("visit_end_hour", 18)
        
        if not pois:
            return json.dumps({"error": "No POIs provided"})
        
        # Validate POI structure
        for poi in pois:
            if not all(key in poi for key in ["name", "lat", "lon"]):
                return json.dumps({"error": "Each POI must have 'name', 'lat', and 'lon' fields"})
            if "duration_min" not in poi:
                poi["duration_min"] = 60  # Default duration
        
        # Order POIs by proximity
        ordered_pois = plan_visit_order(pois)
        
        # Split into days and periods
        schedule = split_into_periods(
            ordered_pois, 
            visit_start_hour=visit_start_hour,
            visit_end_hour=visit_end_hour,
            days=days
        )
        
        return json.dumps({
            "success": True,
            "ordered_pois": ordered_pois,
            "schedule": schedule,
            "total_pois": len(ordered_pois),
            "days": days
        })
        
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Error planning itinerary: {e}"})

# ---------- Tool Definition ----------
itinerary_planner_tool = Tool(
    name="ItineraryPlannerTool",
    func=plan_itinerary_tool_input,
    description=(
        "Organize POIs into an optimized visit plan based on proximity. "
        "Input must be a JSON string with keys: "
        "'pois' (list of POIs with name, lat, lon, duration_min), "
        "'days' (number of days), "
        "'visit_start_hour' (optional, default 9), "
        "'visit_end_hour' (optional, default 18). "
        "Returns JSON with ordered POIs and daily schedule."
    )
)
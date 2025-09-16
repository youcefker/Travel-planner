# travel_planneer/chains/plan_city_trip.py
from tools.web_search_tool import web_search_tool
from tools.places_tool import places_tool
from tools.itinerary_planner_tool import plan_itinerary_tool_input
from tools.booking_flights_tool import booking_flights_tool
from tools.booking_hotels_tool import booking_hotels_tool
import json
import re

def parse_trip_request(user_input: str):
    """
    Extract city, origin, arrival_date, and departure_date from user input.
    Assumes dates are in format YYYY-MM-DD.
    Example: "Plan me a trip from Paris to Barcelona from 2025-06-01 to 2025-06-07"
    """
    city_match = re.search(r"to ([A-Za-z\s]+)", user_input)
    origin_match = re.search(r"from ([A-Za-z\s]+)", user_input)
    arrival_match = re.search(r"(\d{4}-\d{2}-\d{2})", user_input)
    departure_match = re.findall(r"(\d{4}-\d{2}-\d{2})", user_input)

    city = city_match.group(1).strip() if city_match else "Unknown City"
    origin_city = origin_match.group(1).strip() if origin_match else "Unknown Origin"
    arrival_date = arrival_match.group(1) if arrival_match else None
    departure_date = departure_match[1] if len(departure_match) > 1 else None

    return city, origin_city, arrival_date, departure_date


def plan_city_trip(input: str) -> str:
    city, origin_city, arrival_date, departure_date = parse_trip_request(input)

    if not city or city == "Unknown City":
        return json.dumps({"error": "No city found in request"})

    try:
        # 1. Search web for attractions
        search_results = web_search_tool.invoke(f"top attractions to visit in {city}")
        print(f"🔍 Web search results: {search_results}")
        
        # 2. Extract POI names using LLM
        from langchain_openai import ChatOpenAI
        from config import OPENAI_API_KEY, OPENAI_MODEL
        
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
            temperature=0
        )
        
        extraction_prompt = f"""
        Based on the following web search results about {city}, extract the top 5 tourist attractions/points of interest.
        Return ONLY a JSON list of attraction names, nothing else.

        Web search results: {search_results}

        Format: ["Attraction 1", "Attraction 2", "Attraction 3", "Attraction 4", "Attraction 5"]
        """
        
        poi_response = llm.invoke(extraction_prompt)
        print(f"🤖 LLM extracted POIs: {poi_response.content}")
        
        try:
            candidate_pois = json.loads(poi_response.content)
            candidate_pois = [f"{poi}, {city}" for poi in candidate_pois]
        except:
            print("❌ Failed to parse LLM response, using fallback")
            candidate_pois = [f"main attraction in {city}"]

        # 3. Get coordinates for each POI
        pois = []
        for name in candidate_pois:
            try:
                coords_json = places_tool.invoke(name)
                coords = json.loads(coords_json)
                if "error" not in coords:
                    coords["duration_min"] = 90
                    pois.append(coords)
            except:
                continue

        if not pois:
            return json.dumps({"error": f"Could not resolve POIs for {city}"})

        # 4. Create itinerary
        itinerary_input = json.dumps({
            "pois": pois,
            "days": 1,
            "visit_start_hour": 9,
            "visit_end_hour": 18
        })

        result = plan_itinerary_tool_input(itinerary_input)
        result_dict = json.loads(result)

        # 5. Add flights (cheapest)
        flight_results = None
        if origin_city != "Unknown Origin" and arrival_date and departure_date:
            flight_query = json.dumps({
                "from": origin_city,
                "to": city,
                "departDate": arrival_date,
                "returnDate": departure_date,
                "adults": 1,
                "sort": "CHEAPEST"
            })
            try:
                flight_results = booking_flights_tool.invoke(flight_query)
                print(f"✈️ Flights: {flight_results}")
            except Exception as e:
                print(f"❌ Flight search failed: {e}")
                flight_results = {"error": str(e)}

        # 6. Add hotels (cheapest)
        hotel_results = None
        if arrival_date and departure_date:
            hotel_query = json.dumps({
                "city": city,
                "arrival_date": arrival_date,
                "departure_date": departure_date,
                "adults": 1,
                "sort_by": "price"
            })
            try:
                hotel_results = booking_hotels_tool.invoke(hotel_query)
                print(f"🏨 Hotels: {hotel_results}")
            except Exception as e:
                print(f"❌ Hotel search failed: {e}")
                hotel_results = {"error": str(e)}

        # 7. Add context
        result_dict["city"] = city
        result_dict["arrival_date"] = arrival_date
        result_dict["departure_date"] = departure_date
        result_dict["origin_city"] = origin_city
        result_dict["flights"] = flight_results
        result_dict["hotels"] = hotel_results
        result_dict["search_context"] = "Complete trip plan with flights, hotels, itinerary"

        # 8. Generate PDF
        try:
            pdf_path = generate_travel_pdf(result_dict)
            result_dict["pdf_generated"] = pdf_path
        except Exception as e:
            result_dict["pdf_error"] = str(e)
        
        return json.dumps(result_dict)
        
    except Exception as e:
        return json.dumps({"error": f"Error planning trip: {str(e)}"})


def generate_travel_pdf(trip_data):
    """Generate a travel PDF with maps and POI descriptions."""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import os
    from datetime import datetime
    
    city = trip_data.get("city", "Unknown")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_plan_{city}_{timestamp}.pdf"
    filepath = os.path.join(os.getcwd(), filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Travel Plan for {city}", styles['Title']))
    story.append(Spacer(1, 12))

    dates = f"Travel Dates: {trip_data.get('arrival_date')} to {trip_data.get('departure_date')}"
    story.append(Paragraph(dates, styles['Normal']))
    story.append(Spacer(1, 12))

    if trip_data.get("flights"):
        story.append(Paragraph("✈️ Flights", styles['Heading2']))
        story.append(Paragraph(str(trip_data["flights"])[:500], styles['Normal']))
        story.append(Spacer(1, 12))

    if trip_data.get("hotels"):
        story.append(Paragraph("🏨 Hotels", styles['Heading2']))
        story.append(Paragraph(str(trip_data["hotels"])[:500], styles['Normal']))
        story.append(Spacer(1, 12))

    schedule = trip_data.get("schedule", {})
    for day_key, periods in schedule.items():
        story.append(Paragraph(f"📅 {day_key}", styles['Heading2']))
        for period_name, pois in periods.items():
            if pois:
                story.append(Paragraph(f"🕐 {period_name}", styles['Heading3']))
                for poi in pois:
                    poi_text = f"📍 {poi['name']} ({poi.get('duration_min', 60)} mins)"
                    story.append(Paragraph(poi_text, styles['Normal']))
                story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

    doc.build(story)
    return filepath

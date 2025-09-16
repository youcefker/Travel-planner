# travel_planneer/agents/base_agent.py
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from config import OPENAI_API_KEY, OPENAI_MODEL
from tools.booking_flights_tool import booking_flights_tool
from tools.google_transit_tool import google_transit_tool
from tools.booking_hotels_tool import booking_hotels_tool
from tools.rag_tool import rag_tool
from tools.itinerary_planner_tool import itinerary_planner_tool  # Fixed import
from tools.web_search_tool import web_search_tool
from tools.plan_city_trip_tool import plan_city_trip_tool
from tools.places_tool import places_tool

def create_base_agent():
    """
    Creates a basic LangChain agent with GPT and conversation memory.
    """
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model=OPENAI_MODEL,
        temperature=0.3
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    agent = initialize_agent(
        tools=[
            booking_flights_tool, 
            google_transit_tool, 
            booking_hotels_tool, 
            places_tool, 
            rag_tool, 
            web_search_tool, 
            itinerary_planner_tool, 
            plan_city_trip_tool
        ],
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    return agent
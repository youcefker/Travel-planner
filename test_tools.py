# test_individual_tool_invoke.py - Test invoking each tool individually
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tool_invocation():
    """Test invoking each tool with sample input."""
    
    print("🧪 Testing individual tool invocations...")
    print("=" * 50)
    
    # Test 1: Places Tool
    print("\n🔍 Testing Places Tool...")
    try:
        from tools.places_tool import places_tool
        result = places_tool.invoke("Sagrada Familia Barcelona")
        print(f"✅ Places Tool result: {result}")
    except Exception as e:
        print(f"❌ Places Tool failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Web Search Tool
    print("\n🔍 Testing Web Search Tool...")
    try:
        from tools.web_search_tool import web_search_tool
        result = web_search_tool.invoke("Barcelona attractions")
        print(f"✅ Web Search result: {result[:200]}...")  # Truncate output
    except Exception as e:
        print(f"❌ Web Search Tool failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Itinerary Planner Tool
    print("\n🔍 Testing Itinerary Planner Tool...")
    try:
        from tools.itinerary_planner_tool import itinerary_planner_tool
        test_input = '''
        {
            "pois": [
                {"name": "Sagrada Familia", "lat": 41.4036, "lon": 2.1744, "duration_min": 90},
                {"name": "Park Güell", "lat": 41.4145, "lon": 2.1527, "duration_min": 60}
            ],
            "days": 1
        }
        '''
        result = itinerary_planner_tool.invoke(test_input)
        print(f"✅ Itinerary Planner result: {result}")
    except Exception as e:
        print(f"❌ Itinerary Planner Tool failed: {e}")
        import traceback
        traceback.print_exc()

def test_agent_creation_step_by_step():
    """Test agent creation step by step."""
    print("\n🧪 Testing Agent Creation Step by Step...")
    print("=" * 50)
    
    try:
        from langchain.agents import initialize_agent, AgentType
        from langchain_openai import ChatOpenAI
        from langchain.memory import ConversationBufferMemory
        from config import OPENAI_API_KEY, OPENAI_MODEL
        
        print("✅ Imports successful")
        
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
            temperature=0.3
        )
        print("✅ LLM created")
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        print("✅ Memory created")
        
        # Test with empty tools first
        print("🔍 Testing agent with no tools...")
        agent_no_tools = initialize_agent(
            tools=[],
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True
        )
        print("✅ Agent with no tools created successfully")
        
        # Test simple invocation
        response = agent_no_tools.invoke({"input": "Hello"})
        print("✅ Simple invocation successful")
        
        # Now test with one tool at a time
        print("\n🔍 Testing with Places Tool...")
        from tools.places_tool import places_tool
        
        agent_with_places = initialize_agent(
            tools=[places_tool],
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
            verbose=True
        )
        print("✅ Agent with Places Tool created")
        
        # Test the problematic invocation
        print("🔍 Testing problematic query...")
        response = agent_with_places.invoke({"input": "find coordinates for Barcelona"})
        print("✅ Query successful!")
        
    except Exception as e:
        print(f"❌ Agent creation/testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_invocation()
    test_agent_creation_step_by_step()
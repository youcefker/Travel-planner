# travel_planneer/main.py
from agents.base_agent import create_base_agent

def run():
    print("🔧 Creating agent...")
    try:
        agent = create_base_agent()
        print("✅ Agent created successfully!")
        
        # Debug: Print agent tools
        print("🔍 Available tools:")
        for tool in agent.tools:
            print(f"  - {tool.name}: {tool.description}")
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n🤖 AI Travel Planner (basic agent)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        print(f"🔍 User input: {user_input}")
        print(f"🔍 Invoking agent with: {{'input': '{user_input}'}}")
        
        try:
            response = agent.invoke({"input": user_input})
            print(f"✅ Agent response: {response}\n")
        except Exception as e:
            print(f"❌ Error during agent invocation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run()
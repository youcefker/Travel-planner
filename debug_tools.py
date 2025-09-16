# debug_tool_inputs.py - Check what input each tool expects
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_tool_schemas():
    """Check the input schema of each tool."""
    
    tools_to_check = [
        ("places_tool", "tools.places_tool", "places_tool"),
        ("web_search_tool", "tools.web_search_tool", "web_search_tool"),
        ("itinerary_planner_tool", "tools.itinerary_planner_tool", "itinerary_planner_tool"),
        ("plan_city_trip_tool", "tools.plan_city_trip_tool", "plan_city_trip_tool"),
    ]
    
    for tool_name, module_path, tool_var in tools_to_check:
        try:
            print(f"\n🔍 Checking {tool_name}...")
            
            module = __import__(module_path, fromlist=[tool_var])
            tool = getattr(module, tool_var)
            
            print(f"  📝 Name: {tool.name}")
            print(f"  📝 Description: {tool.description}")
            
            # Check if tool has input schema
            if hasattr(tool, 'args_schema'):
                print(f"  📋 Has args_schema: {tool.args_schema}")
                if tool.args_schema:
                    try:
                        schema_fields = tool.args_schema.__fields__ if hasattr(tool.args_schema, '__fields__') else 'Unknown'
                        print(f"  📋 Schema fields: {schema_fields}")
                    except:
                        print(f"  📋 Schema: {tool.args_schema}")
            else:
                print(f"  📋 No args_schema (expects string input)")
            
            # Check the function signature
            import inspect
            try:
                sig = inspect.signature(tool.func)
                print(f"  🔧 Function signature: {sig}")
            except:
                print(f"  🔧 Could not get function signature")
                
        except Exception as e:
            print(f"  ❌ Error checking {tool_name}: {e}")

if __name__ == "__main__":
    check_tool_schemas()
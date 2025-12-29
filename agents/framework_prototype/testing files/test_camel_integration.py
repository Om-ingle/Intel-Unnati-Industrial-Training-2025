import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import State
from nodes.external_nodes import CamelNode

def test_camel_node():
    print("="*60)
    print("TEST: CamelNode Execution")
    print("="*60)
    
    # 1. Setup State
    state = State()
    state.set("customer_id", "CUST-1001")
    
    # 2. Configure Node
    node = CamelNode("camel_test_node", config={
        "camel_url": "http://localhost:9999", # Intentionally wrong port to trigger mock
        "route_id": "api/sap/customer",
        "payload": {"id": "{customer_id}", "request": "get_details"},
        "output_key": "sap_data"
    })
    
    # 3. Execute
    print("\n[Executing Node]...")
    result = node.execute(state)
    
    # 4. Verify
    print(f"\n[Result Status]: {result.status}")
    print(f"[Output]: {result.output}")
    
    if result.status.value == "success":
        print("✅ CamelNode successfully handled execution (Mock fallback works)")
    else:
        print("❌ CamelNode failed")

if __name__ == "__main__":
    test_camel_node()

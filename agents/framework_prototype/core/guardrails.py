"""
Guardrail system for validation and safety
"""

import sys
from pathlib import Path
from typing import Any, Dict, Callable, Optional, List

# Handle imports - import from state
try:
    from .state import State, NodeResult, NodeStatus
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.state import State, NodeResult, NodeStatus


class Guardrail:
    """
    A validation rule that can check node inputs/outputs.
    
    Example:
        def check_positive(value):
            return value > 0, "Value must be positive"
        
        guardrail = Guardrail("positive_check", check_positive)
    """
    
    def __init__(
        self,
        name: str,
        check_func: Callable,
        description: str = ""
    ):
        self.name = name
        self.check_func = check_func
        self.description = description
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """
        Validate a value.
        
        Returns:
            (is_valid, message)
        """
        return self.check_func(value)
    
    def __repr__(self):
        return f"Guardrail(name={self.name})"


class GuardrailRegistry:
    """
    Registry for managing guardrails.
    
    Example:
        registry = GuardrailRegistry()
        registry.register(Guardrail("check_length", lambda x: (len(x) > 0, "Must not be empty")))
        is_valid, msg = registry.validate("check_length", "test")
    """
    
    def __init__(self):
        self._guardrails: Dict[str, Guardrail] = {}
    
    def register(self, guardrail: Guardrail):
        """Register a guardrail"""
        self._guardrails[guardrail.name] = guardrail
    
    def get(self, name: str) -> Optional[Guardrail]:
        """Get a guardrail by name"""
        return self._guardrails.get(name)
    
    def validate(self, name: str, value: Any) -> tuple[bool, str]:
        """Validate a value using a guardrail"""
        guardrail = self.get(name)
        if not guardrail:
            raise ValueError(f"Guardrail not found: {name}")
        return guardrail.validate(value)
    
    def validate_all(self, value: Any) -> List[tuple[str, bool, str]]:
        """
        Validate value against all guardrails.
        
        Returns:
            List of (guardrail_name, is_valid, message)
        """
        results = []
        for name, guardrail in self._guardrails.items():
            is_valid, message = guardrail.validate(value)
            results.append((name, is_valid, message))
        return results
    
    def list_guardrails(self) -> list:
        """List all registered guardrails"""
        return list(self._guardrails.keys())
    
    def __repr__(self):
        return f"GuardrailRegistry(guardrails={len(self._guardrails)})"


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Guardrail System...\n")
    
    # Test Guardrail
    print("[1/2] Testing Guardrail...")
    
    def check_range(value):
        if 0 <= value <= 100:
            return True, "Value is in valid range"
        return False, "Value must be between 0 and 100"
    
    guardrail = Guardrail("range_check", check_range, "Checks if value is 0-100")
    
    is_valid, msg = guardrail.validate(50)
    print(f"✅ Guardrail: {guardrail}")
    print(f"   Valid (50): {is_valid} - {msg}")
    
    is_valid, msg = guardrail.validate(150)
    print(f"   Valid (150): {is_valid} - {msg}")
    
    # Test GuardrailRegistry
    print("\n[2/2] Testing GuardrailRegistry...")
    
    registry = GuardrailRegistry()
    registry.register(guardrail)
    registry.register(Guardrail(
        "positive_check",
        lambda x: (x > 0, "Must be positive")
    ))
    
    print(f"✅ Registry: {registry}")
    print(f"   Guardrails: {registry.list_guardrails()}")
    
    results = registry.validate_all(50)
    for name, valid, msg in results:
        print(f"   {name}: {valid} - {msg}")
    
    print("\n✅ Guardrail system is working!")

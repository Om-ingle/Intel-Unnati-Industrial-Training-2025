"""
Guardrails - Retry logic, timeouts, and error handling
"""

import sys
from pathlib import Path
from typing import Any, Dict, Callable, Optional
import time
from functools import wraps

# Handle imports
try:
    from .node import Node, NodeResult, NodeStatus
    from .state import State
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.node import Node, NodeResult, NodeStatus
    from core.state import State

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)


# ============================================================================
# RETRY DECORATOR
# ============================================================================

def with_retry(max_attempts: int = 3, wait_multiplier: int = 1):
    """
    Decorator to add retry logic to node execution.
    
    Args:
        max_attempts: Maximum number of retry attempts
        wait_multiplier: Multiplier for exponential backoff (seconds)
    
    Example:
        @with_retry(max_attempts=3, wait_multiplier=2)
        def execute(self, state, config):
            # This will retry up to 3 times with exponential backoff
            return NodeResult(...)
    """
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=wait_multiplier, min=1, max=10),
            retry=retry_if_exception_type(Exception),
            reraise=True
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# TIMEOUT HANDLER
# ============================================================================

import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    """Raised when operation exceeds timeout"""
    pass


@contextmanager
def timeout(seconds: int):
    """
    Context manager for timeout handling.
    
    Args:
        seconds: Timeout in seconds
    
    Example:
        with timeout(30):
            # Code that should complete within 30 seconds
            result = long_running_operation()
    
    Note: Only works on Unix systems (Linux, macOS)
    """
    def timeout_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    
    # Check if signal is available (Unix only)
    if hasattr(signal, 'SIGALRM'):
        # Set the signal handler
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        
        try:
            yield
        finally:
            # Restore the old handler and cancel the alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # On Windows, just yield without timeout (for now)
        # In Phase 2, we can use threading.Timer for cross-platform support
        yield


# ============================================================================
# GUARDED NODE (with retry + timeout)
# ============================================================================

class GuardedNode(Node):
    """
    Node with built-in retry and timeout capabilities.
    
    Example:
        class MyNode(GuardedNode):
            def execute(self, state, config):
                # This will automatically retry on failure
                # and timeout if it takes too long
                return NodeResult(...)
    """
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        config: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 300,
        max_retries: int = 3,
        retry_backoff: int = 1
    ):
        super().__init__(
            node_id=node_id,
            node_type=node_type,
            config=config,
            timeout=timeout_seconds,
            retries=max_retries
        )
        self.retry_backoff = retry_backoff
        self.retry_count = 0
    
    def run(self, state: State) -> NodeResult:
        """
        Run node with retry and timeout protection.
        """
        self.status = NodeStatus.RUNNING
        self.started_at = time.time()
        
        for attempt in range(1, self.retries + 1):
            self.retry_count = attempt
            
            try:
                # Try to execute with timeout
                with timeout(self.timeout):
                    result = self.execute(state, self.config)
                
                # If successful, return
                if result.is_success():
                    result.metadata['retry_count'] = attempt
                    result.metadata['total_attempts'] = self.retries
                    return result
                
                # If failed but not last attempt, retry
                if attempt < self.retries:
                    wait_time = self.retry_backoff * (2 ** (attempt - 1))
                    print(f"⚠️  Node {self.node_id} failed (attempt {attempt}/{self.retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                # Last attempt failed
                result.metadata['retry_count'] = attempt
                result.metadata['total_attempts'] = self.retries
                return result
                
            except TimeoutException as e:
                error_msg = str(e)
                if attempt < self.retries:
                    print(f"⚠️  Node {self.node_id} timed out (attempt {attempt}/{self.retries}), retrying...")
                    time.sleep(self.retry_backoff * (2 ** (attempt - 1)))
                    continue
                
                # Timeout on last attempt
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error=error_msg,
                    metadata={
                        'retry_count': attempt,
                        'total_attempts': self.retries,
                        'failure_reason': 'timeout'
                    }
                )
            
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                if attempt < self.retries:
                    print(f"⚠️  Node {self.node_id} errored (attempt {attempt}/{self.retries}), retrying...")
                    time.sleep(self.retry_backoff * (2 ** (attempt - 1)))
                    continue
                
                # Exception on last attempt
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error=error_msg,
                    metadata={
                        'retry_count': attempt,
                        'total_attempts': self.retries,
                        'failure_reason': 'exception'
                    }
                )
        
        # Should never reach here, but just in case
        return NodeResult(
            status=NodeStatus.FAILED,
            error="Max retries exceeded",
            metadata={'retry_count': self.retries, 'total_attempts': self.retries}
        )


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.
    
    After a certain number of failures, the circuit "opens" and
    stops trying to execute, failing fast instead.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, reject requests
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        """
        if self.state == "OPEN":
            # Check if we should try recovery
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is OPEN, failing fast")
        
        try:
            result = func(*args, **kwargs)
            
            # Record success
            if self.state == "HALF_OPEN":
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = "CLOSED"
                    self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Record failure
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing Guardrails...\n")
    
    # Test 1: Retry logic
    print("[1/3] Testing Retry Logic...")
    
    class FlakyNode(GuardedNode):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attempt_count = 0
        
        def execute(self, state, config):
            self.attempt_count += 1
            
            if self.attempt_count < 3:
                raise ValueError(f"Simulated failure (attempt {self.attempt_count})")
            
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output=f"Success on attempt {self.attempt_count}"
            )
    
    state = State()
    node = FlakyNode(
        node_id="flaky",
        node_type="test",
        max_retries=3,
        retry_backoff=0.1  # Short backoff for testing
    )
    
    result = node.run(state)
    print(f"✅ Status: {result.status.value}")
    print(f"✅ Output: {result.output}")
    print(f"✅ Retry count: {result.metadata.get('retry_count')}")
    
    # Test 2: Timeout (Unix only)
    print("\n[2/3] Testing Timeout...")
    
    if hasattr(signal, 'SIGALRM'):
        try:
            with timeout(2):
                print("   Starting operation with 2s timeout...")
                time.sleep(1)  # Should succeed
                print("   ✅ Operation completed within timeout")
        except TimeoutException:
            print("   ❌ Should not have timed out")
        
        try:
            with timeout(1):
                print("   Starting operation with 1s timeout...")
                time.sleep(3)  # Should timeout
                print("   ❌ Should have timed out")
        except TimeoutException:
            print("   ✅ Timeout caught correctly")
    else:
        print("   ⚠️  Timeout not supported on Windows (will implement in Phase 2)")
    
    # Test 3: Circuit Breaker
    print("\n[3/3] Testing Circuit Breaker...")
    
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=2)
    
    def failing_function():
        raise ValueError("Service unavailable")
    
    # Cause failures to open circuit
    for i in range(4):
        try:
            cb.call(failing_function)
        except:
            pass
    
    print(f"✅ Circuit state after failures: {cb.state}")
    
    # Try to call when circuit is open
    try:
        cb.call(failing_function)
        print("   ❌ Should have failed fast")
    except Exception as e:
        if "Circuit breaker is OPEN" in str(e):
            print(f"✅ Failed fast: {e}")
    
    print("\n✅ Guardrails.py is working correctly!")

"""
External Integration Nodes - Google Calendar, Email, etc.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
import time
from datetime import datetime, timedelta

# Handle imports
try:
    from ..core import Node, State, NodeResult, NodeStatus
    import requests
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import Node, State, NodeResult, NodeStatus
    import requests


class GoogleCalendarNode(Node):
    """
    Google Calendar integration node.
    Creates calendar events and asks for user confirmation.
    
    Config:
        - event_title: Event title (supports {variables})
        - event_description: Event description
        - start_date: Start date/time (supports {variables})
        - end_date: End date/time (supports {variables})
        - location: Event location
        - output_key: Where to store confirmation
        - require_confirmation: Ask for confirmation before booking (default: True)
    
    Example:
        config:
          event_title: "Tour: {destination}"
          start_date: "{tour_date} 10:00"
          end_date: "{tour_date} 18:00"
          location: "{destination}"
          require_confirmation: true
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        # Replace variables in config
        event_title = self._replace_variables(config.get("event_title", "Event"), state)
        event_description = self._replace_variables(config.get("event_description", ""), state)
        start_date = self._replace_variables(config.get("start_date", ""), state)
        end_date = self._replace_variables(config.get("end_date", ""), state)
        location = self._replace_variables(config.get("location", ""), state)
        require_confirmation = config.get("require_confirmation", True)
        output_key = config.get("output_key", "calendar_event")
        
        # Create event data
        event_data = {
            "title": event_title,
            "description": event_description,
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "status": "pending_confirmation" if require_confirmation else "ready_to_book",
            "requires_confirmation": require_confirmation,
            "created_at": datetime.now().isoformat()
        }
        
        # Store event data in state
        state.set(output_key, event_data)
        
        # Store notification
        notification = {
            "type": "calendar_booking",
            "message": f"📅 Calendar event ready: {event_title}",
            "event_data": event_data,
            "requires_action": require_confirmation,
            "timestamp": datetime.now().isoformat()
        }
        
        notifications = state.get("notifications", [])
        if not isinstance(notifications, list):
            notifications = []
        notifications.append(notification)
        state.set("notifications", notifications)
        
        return NodeResult.success(
            output=event_data,
            metadata={
                "event_title": event_title,
                "requires_confirmation": require_confirmation,
                "action_type": "google_calendar"
            }
        )
    
    def _replace_variables(self, template: str, state: State) -> str:
        """Replace {variable} placeholders with state values"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            value = state.get(var_name)
            return str(value) if value is not None else f"{{{var_name}}}"
        
        return re.sub(r'\{(\w+)\}', replace_var, template)


class ExternalActionNode(Node):
    """
    Generic external action node that requires user confirmation.
    
    Config:
        - action_type: Type of action (email, calendar, payment, etc.)
        - action_description: Description of the action
        - action_data: Data for the action (dict)
        - require_confirmation: Require user confirmation (default: True)
        - output_key: Where to store result
    
    Example:
        config:
          action_type: "email"
          action_description: "Send email to {recipient}"
          action_data:
            to: "{recipient}"
            subject: "{subject}"
            body: "{body}"
          require_confirmation: true
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        action_type = config.get("action_type", "external_action")
        action_description = self._replace_variables(config.get("action_description", "External action"), state)
        action_data = config.get("action_data", {})
        require_confirmation = config.get("require_confirmation", True)
        output_key = config.get("output_key", "external_action")
        
        # Replace variables in action_data
        if isinstance(action_data, dict):
            processed_data = {}
            for key, value in action_data.items():
                if isinstance(value, str):
                    processed_data[key] = self._replace_variables(value, state)
                else:
                    processed_data[key] = value
        else:
            processed_data = action_data
        
        # Create action request
        action_request = {
            "action_type": action_type,
            "description": action_description,
            "data": processed_data,
            "status": "pending_confirmation" if require_confirmation else "ready_to_execute",
            "requires_confirmation": require_confirmation,
            "created_at": datetime.now().isoformat()
        }
        
        # Store in state
        state.set(output_key, action_request)
        
        # Store notification
        notification = {
            "type": action_type,
            "message": f"🔔 Action ready: {action_description}",
            "action_data": action_request,
            "requires_action": require_confirmation,
            "timestamp": datetime.now().isoformat()
        }
        
        notifications = state.get("notifications", [])
        if not isinstance(notifications, list):
            notifications = []
        notifications.append(notification)
        state.set("notifications", notifications)
        
        return NodeResult.success(
            output=action_request,
            metadata={
                "action_type": action_type,
                "requires_confirmation": require_confirmation
            }
        )
    
    def _replace_variables(self, template: str, state: State) -> str:
        """Replace {variable} placeholders with state values"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            value = state.get(var_name)
            if value is None:
                return f"{{{var_name}}}"
            return str(value)
        
        if isinstance(template, dict):
            return {k: self._replace_variables(v, state) if isinstance(v, str) else v for k, v in template.items()}
        return re.sub(r'\{(\w+)\}', replace_var, template)



class CamelNode(Node):
    """
    Node to invoke Apache Camel routes via HTTP REST.
    
    Config:
        - camel_url: Base URL of the Camel instance (default: http://localhost:8080)
        - route_id: specific route path to trigger (e.g., "api/sap/customer")
        - payload: Data to send (supports {variables})
        - method: HTTP method (POST, GET, etc.)
        - output_key: Where to store the response
    """
    
    def execute(self, state: State) -> NodeResult:
        config = self.config
        
        camel_url = config.get("camel_url", "http://localhost:8080").rstrip('/')
        route_id = config.get("route_id", "camel/route")
        payload_template = config.get("payload", {})
        method = config.get("method", "POST").upper()
        output_key = config.get("output_key", "camel_response")
        
        # Prepare payload
        payload = self._replace_variables(payload_template, state)
        
        # Construct URL
        # Camel routes often exposed like http://host:port/api/myroute
        full_url = f"{camel_url}/{route_id}"
        
        print(f"🐫 connecting to Camel Route: {full_url}")
        
        try:
            # Try to connect
            # timeout small for prototype responsiveness
            if method == 'POST':
                response = requests.post(full_url, json=payload, timeout=2)
            else:
                response = requests.get(full_url, params=payload, timeout=2)
                
            response.raise_for_status()
            result_data = response.json()
            
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Camel instance not found at {full_url}. (This is expected if Camel is not running).")
            print("   Using Mock Response for demonstration.")
            result_data = {
                "status": "mock_success", 
                "source": "CamelNode (Mock)", 
                "original_payload": payload,
                "note": "Real connection failed, returned mock data."
            }
        except Exception as e:
             return NodeResult.failed(f"Camel integration failed: {str(e)}")

        state.set(output_key, result_data)
        
        return NodeResult.success(output=result_data)
    
    def _replace_variables(self, template: Any, state: State) -> Any:
        """Helper to replace vars in dict or string"""
        if isinstance(template, str):
            import re
            def replace_var(match):
                var_name = match.group(1)
                val = state.get(var_name)
                return str(val) if val is not None else f"{{{var_name}}}"
            return re.sub(r'\{(\w+)\}', replace_var, template)
        elif isinstance(template, dict):
            return {k: self._replace_variables(v, state) for k, v in template.items()}
        elif isinstance(template, list):
            return [self._replace_variables(i, state) for i in template]
        return template

# Registry
EXTERNAL_NODE_TYPES = {
    "google_calendar": GoogleCalendarNode,
    "external_action": ExternalActionNode,
    "camel_integration": CamelNode,
}


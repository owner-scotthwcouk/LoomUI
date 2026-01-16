from typing import Dict, List, Any

class ReactiveState:
    """
    A smart object that notifies the UI when its attributes change.
    """
    def __init__(self):
        # Store actual values in a private dict
        self._values = {}
        # Keep track of which Component IDs are watching which variable name
        self._listeners: Dict[str, List[str]] = {}
        # Reference to the app so we can send updates
        self._app_ref = None

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._values[name] = value
            # NOTIFY: If anyone is listening to this variable, update them!
            if self._app_ref and name in self._listeners:
                for comp_id in self._listeners[name]:
                    self._app_ref.push_update(comp_id, value)

    def __getattr__(self, name: str):
        try:
            return self._values[name]
        except KeyError:
            # Return empty string to prevent crashes if accessed early
            return ""

    def bind(self, key: str, component_id: str):
        """Link a UI component to a state variable."""
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(component_id)
        # Return current value if it exists
        return self._values.get(key, "")

# Create the global instance
state = ReactiveState()
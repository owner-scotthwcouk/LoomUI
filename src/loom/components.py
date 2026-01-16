import uuid
from .state import state

# The Context Stack (Global) to handle nesting
CONTEXT_STACK = []

class Component:
    def __init__(self, id: str = None):
        self.id = id or f"comp_{str(uuid.uuid4())[:8]}"
        self.type = self.__class__.__name__
        self.children = []
        
        # Auto-Attach: If we are inside a context manager, add self to parent
        if CONTEXT_STACK:
            parent = CONTEXT_STACK[-1]
            parent.children.append(self)

    def to_json(self):
        return {
            "id": self.id, 
            "type": self.type, 
            "children": [c.to_json() for c in self.children]
        }

class Container(Component):
    """Base class for things that hold other things (Rows, Columns)."""
    def __enter__(self):
        CONTEXT_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CONTEXT_STACK.pop()

class Column(Container):
    pass

class Row(Container):
    pass

class Text(Component):
    def __init__(self, value, id: str = None):
        super().__init__(id)
        self.value = value
        self.state_key = None
        
        # Simple binding logic: if value starts with "$", it's a state key
        if isinstance(value, str) and value.startswith("$"):
            key = value[1:] # remove $
            self.state_key = key
            # Register this component as a listener
            state.bind(key, self.id)
            # Set initial value from state
            self.value = getattr(state, key)

    def to_json(self):
        return {**super().to_json(), "value": str(self.value)}

class Button(Component):
    def __init__(self, label: str, on_click, id: str = None):
        super().__init__(id)
        self.label = label
        self.on_click = on_click

    def to_json(self):
        return {**super().to_json(), "label": self.label}

class Input(Component):
    def __init__(self, value="", id: str = None):
        super().__init__(id)
        self.value = value
        self.state_key = None
        
        # Binding Logic
        if isinstance(value, str) and value.startswith("$"):
            self.state_key = value[1:]
            # Register listener (optional for input, but good for two-way binding)
            state.bind(self.state_key, self.id)
            self.value = getattr(state, self.state_key)

    def handle_input(self, new_value):
        """Called when user types in the browser."""
        self.value = new_value
        # If bound to state, update the global state automatically
        if self.state_key:
            setattr(state, self.state_key, new_value)

    def to_json(self):
        return {**super().to_json(), "value": str(self.value)}

class Chart(Component):
    def __init__(self, type="bar", data=None, labels=None, id: str = None):
        super().__init__(id)
        self.chart_type = type  # e.g., 'bar', 'line', 'pie'
        self.data = data or []  # e.g., [10, 20, 30]
        self.labels = labels or [] # e.g., ["Jan", "Feb", "Mar"]

    def to_json(self):
        return {
            **super().to_json(),
            "chartType": self.chart_type,
            "data": self.data,
            "labels": self.labels
        }
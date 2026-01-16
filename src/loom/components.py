# D:\Dev\Loom-UI\src\loom\components.py
import re
from .state import state, current_context, component_registry

class Component:
    """Base class for all UI components."""
    def __init__(self):
        # Register every component by ID
        self.id = id(self)
        component_registry[self.id] = self

    def to_dict(self):
        return {"type": self.__class__.__name__, "id": self.id}

class Text(Component):
    def __init__(self, content, size=None, weight=None, color=None):
        super().__init__()
        self.content = content
        self.size = size
        self.weight = weight
        self.color = color

    def render_content(self):
        """
        The Magic: Finds words starting with $ and replaces them 
        with the actual value from the global state.
        """
        text = str(self.content)
        
        # Regex to find variables like $count or $status
        matches = re.findall(r"\$(\w+)", text)
        
        for var_name in matches:
            if hasattr(state, var_name):
                val = getattr(state, var_name)
                # Swap "$var" with the actual value
                text = text.replace(f"${var_name}", str(val))
            else:
                text = text.replace(f"${var_name}", "?")
        return text

    def render_prop(self, prop_value):
        """Helper to allow properties like color='$status_color'"""
        if prop_value and isinstance(prop_value, str) and prop_value.startswith("$"):
            var_name = prop_value[1:]
            if hasattr(state, var_name):
                return getattr(state, var_name)
        return prop_value

    def to_dict(self):
        return {
            "type": "Text",
            "id": self.id,
            "content": self.render_content(), 
            "props": {
                "size": self.size,
                "weight": self.weight,
                "color": self.render_prop(self.color)
            }
        }

class Button(Component):
    def __init__(self, label, on_click=None, variant="primary"):
        super().__init__()
        self.label = label
        self.on_click = on_click
        self.variant = variant

    def to_dict(self):
        return {
            "type": "Button",
            "id": self.id,
            "label": self.label,
            "props": {"variant": self.variant}
        }

class Input(Component):
    def __init__(self, value_var, label=None, type="text"):
        super().__init__()
        self.value_var = value_var
        self.label = label
        self.type = type

    def to_dict(self):
        return {
            "type": "Input",
            "id": self.id,
            "props": {
                "label": self.label, 
                "value": getattr(state, self.value_var, ""),
                "variable": self.value_var,
                "type": self.type
            }
        }

class Chart(Component):
    def __init__(self, data_var, type="bar", title=None):
        super().__init__()
        self.data_var = data_var
        self.type = type
        self.title = title

    def to_dict(self):
        chart_data = getattr(state, self.data_var, [])
        return {
            "type": "Chart",
            "id": self.id,
            "props": {
                "type": self.type,
                "title": self.title,
                "data": chart_data
            }
        }

# --- Layout Components ---

class Row(Component):
    def __init__(self):
        super().__init__()
        self.children = []

    def __enter__(self):
        current_context.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        current_context.pop()

    def add(self, component):
        self.children.append(component)

    def to_dict(self):
        return {
            "type": "Row",
            "id": self.id,
            "children": [child.to_dict() for child in self.children]
        }

class Column(Component):
    def __init__(self):
        super().__init__()
        self.children = []

    def __enter__(self):
        current_context.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        current_context.pop()

    def add(self, component):
        self.children.append(component)

    def to_dict(self):
        return {
            "type": "Column",
            "id": self.id,
            "children": [child.to_dict() for child in self.children]
        }

class Card(Component):
    def __init__(self):
        super().__init__()
        self.children = []

    def __enter__(self):
        current_context.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        current_context.pop()

    def add(self, component):
        self.children.append(component)

    def to_dict(self):
        return {
            "type": "Card",
            "id": self.id,
            "children": [child.to_dict() for child in self.children]
        }
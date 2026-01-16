# src/loom/components.py
import uuid
from .state import current_context, state

class Component:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.children = []
        self.type = "Component"
    def add(self, component): self.children.append(component)
    def to_dict(self): return {"id": self.id, "type": self.type, "children": [c.to_dict() for c in self.children]}
    def __enter__(self): current_context.append(self); return self
    def __exit__(self, exc_type, exc_val, exc_tb): current_context.pop()

# --- Layouts ---
class Page(Component):
    def __init__(self, name): super().__init__(); self.type = "Page"; self.name = name
    def to_dict(self):
        if getattr(state, "active_page", "") != self.name: return {"id": self.id, "type": "Hidden"}
        return super().to_dict()

class Column(Component):
    def __init__(self): super().__init__(); self.type = "Column"
class Row(Component):
    def __init__(self): super().__init__(); self.type = "Row"
class Card(Component):
    def __init__(self, title=""): super().__init__(); self.type = "Card"; self.title = title
    def to_dict(self): d = super().to_dict(); d['title'] = self.title; return d
class Navbar(Component):
    def __init__(self, title=""): super().__init__(); self.type = "Navbar"; self.title = title
    def to_dict(self): d = super().to_dict(); d['title'] = self.title; return d
class Sidebar(Component):
    def __init__(self): super().__init__(); self.type = "Sidebar"
class Modal(Component):
    def __init__(self, open_var): super().__init__(); self.type = "Modal"; self.open_var = open_var
    def to_dict(self): d = super().to_dict(); d['is_open'] = getattr(state, self.open_var, False); return d

# --- Widgets ---
class Text(Component):
    def __init__(self, content, color="inherit", size="base"):
        super().__init__(); self.type = "Text"; self.content = content; self.color = color; self.size = size
    def to_dict(self): return {"id": self.id, "type": self.type, "content": resolve_text(self.content), "color": resolve_color(self.color), "size": self.size}

class Button(Component):
    def __init__(self, label, on_click=None, variant="primary"):
        super().__init__(); self.type = "Button"; self.label = label; self.on_click = on_click; self.variant = variant
        from .state import component_registry
        component_registry[self.id] = self
    def to_dict(self): return {"id": self.id, "type": self.type, "label": self.label, "variant": resolve_text(self.variant)}

class Input(Component):
    def __init__(self, value_var, placeholder="..."):
        super().__init__(); self.type = "Input"; self.value_var = value_var; self.placeholder = placeholder
        from .state import component_registry
        component_registry[self.id] = self
    def to_dict(self): return {"id": self.id, "type": self.type, "value": getattr(state, self.value_var, ""), "placeholder": self.placeholder}

class Select(Component):
    def __init__(self, value_var, options):
        super().__init__(); self.type = "Select"; self.value_var = value_var; self.options = options
        from .state import component_registry
        component_registry[self.id] = self
    def to_dict(self): return {"id": self.id, "type": self.type, "value": getattr(state, self.value_var, ""), "options": self.options}

class Metric(Component):
    def __init__(self, label, value, trend=None, color="blue"):
        super().__init__(); self.type = "Metric"; self.label = label; self.value = value; self.trend = trend; self.color = color
    def to_dict(self): return {"id": self.id, "type": self.type, "label": self.label, "value": resolve_text(str(self.value)), "trend": self.trend, "color": self.color}

class Chart(Component):
    def __init__(self, data_var, title="", color="rgb(75, 192, 192)"):
        super().__init__(); self.type = "Chart"; self.data_var = data_var; self.title = title; self.color = color
    def to_dict(self): return {"id": self.id, "type": self.type, "data": getattr(state, self.data_var, []), "labels": [str(i) for i in range(len(getattr(state, self.data_var, [])))], "title": self.title, "color": self.color}

class Table(Component):
    def __init__(self, data_var, headers): super().__init__(); self.type = "Table"; self.data_var = data_var; self.headers = headers
    def to_dict(self): return {"id": self.id, "type": self.type, "headers": self.headers, "rows": getattr(state, self.data_var, [])}

class ProgressBar(Component):
    def __init__(self, value_var, color="blue"): super().__init__(); self.type = "ProgressBar"; self.value_var = value_var; self.color = color
    def to_dict(self): return {"id": self.id, "type": self.type, "value": float(getattr(state, self.value_var, 0)), "color": self.color}

# --- Helpers ---
def resolve_text(text):
    if "$" in text:
        return " ".join([str(getattr(state, w[1:].replace("%",""), w)) + ("%" if "%" in w else "") if w.startswith("$") else w for w in text.split()])
    return text
def resolve_color(color): return getattr(state, color[1:], "inherit") if color.startswith("$") else color
# D:\Dev\Loom-UI\src\loom\state.py

class State:
    def __init__(self):
        # Stores the actual variable values
        self.__dict__["_data"] = {}

    def __getattr__(self, name):
        # Return the value if it exists, otherwise return "$name" string
        return self._data.get(name, f"${name}")

    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self._data[name] = value

# The global state instance
state = State()

# GLOBAL REGISTRIES (Moved here to stop circular imports)
# 1. Keeps track of "with app.Row():" nesting
current_context = [] 

# 2. Keeps track of Buttons so we can find their 'on_click' functions later
component_registry = {}
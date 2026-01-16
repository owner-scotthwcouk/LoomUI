# src/loom/state.py
from contextlib import contextmanager

class State:
    def __init__(self):
        self.__dict__["_data"] = {}
        self.__dict__["_listeners"] = []
        self.__dict__["_batch_active"] = False

    def __getattr__(self, name):
        return self._data.get(name, f"${name}")

    def __setattr__(self, name, value):
        if name in ["_data", "_listeners", "_batch_active"]:
            super().__setattr__(name, value)
        else:
            self._data[name] = value
            if not self._batch_active: self._notify()

    def _notify(self):
        for listener in self._listeners:
            try: listener()
            except: pass

    def add_listener(self, func):
        self._listeners.append(func)

    @contextmanager
    def batch_update(self):
        self._batch_active = True
        try: yield
        finally:
            self._batch_active = False
            self._notify()

state = State()
current_context = [] 
component_registry = {}
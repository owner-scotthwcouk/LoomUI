import inspect
from .components import Column, Text, Input, Button, Row
from .state import state

def expose(func):
    """
    Decorator: Takes a python function and returns a UI Component (Column)
    containing inputs for arguments, a run button, and an output display.
    """
    # 1. Analyze the function
    sig = inspect.signature(func)
    func_name = func.__name__
    
    # 2. Create unique state keys for this function
    # e.g. "calculate_roi_input_investment"
    inputs = {}
    for param_name in sig.parameters:
        state_key = f"{func_name}_in_{param_name}"
        inputs[param_name] = state_key
        # Initialize state to empty string
        setattr(state, state_key, "")
    
    result_key = f"{func_name}_result"
    setattr(state, result_key, "Ready")

    # 3. Define the "Runner" function
    def run_logic():
        # Gather values from state
        kwargs = {}
        for param_name, key in inputs.items():
            val = getattr(state, key)
            # Auto-convert to int/float if type hint exists
            hint = sig.parameters[param_name].annotation
            if hint is int:
                try: val = int(val)
                except: val = 0
            elif hint is float:
                try: val = float(val)
                except: val = 0.0
            kwargs[param_name] = val
        
        # Run user function
        res = func(**kwargs)
        setattr(state, result_key, str(res))

    # 4. Build the UI Tree
    container = Column()
    with container:
        Text(f"Function: {func_name.replace('_', ' ').title()}")
        
        # Create inputs
        for param_name in inputs:
            with Row():
                Text(f"{param_name}: ")
                Input(value=f"${inputs[param_name]}")
        
        Button("Run", on_click=run_logic)
        Text(f"Result: ")
        Text(f"${result_key}") # Bind to result
        
    return container
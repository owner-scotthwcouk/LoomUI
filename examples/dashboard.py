from loom import LoomApp, state

# Initialize
app = LoomApp()

# Define State
state.count = 0
state.message = "Start clicking!"

# Define Logic
def increment():
    state.count += 1
    state.message = f"You clicked {state.count} times"

def reset():
    state.count = 0
    state.message = "Reset done."

# --- THE FIX IS HERE ---
# We use 'app.root' (the main window) instead of creating a new 'app.Column()'
# This ensures the buttons are actually added to the page being rendered.
with app.root:
    
    app.Text("LoomUI v0.1 Demo")
    
    with app.Row():
        app.Button("Count Up", on_click=increment)
        app.Button("Reset", on_click=reset)
    
    # Dynamic Text (bound to state variables)
    app.Text("$message")
    
if __name__ == "__main__":
    app.run()
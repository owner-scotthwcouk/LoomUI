from loom_ui_pkg import LoomApp, state
import random

# Initialize the app
app = LoomApp()

# --- 1. THE STATE (Invisible Monitoring) ---
# We just declare variables. No session_state['key'] needed.
state.visits = 0
state.server_status = "ONLINE"
state.status_color = "#00ff00"  # Neon Green

# --- 2. THE LOGIC (Pure Python) ---
def simulate_traffic():
    """Simulates a hit to the server."""
    state.visits += 1
    
    # Simple logic to change UI appearance dynamically
    if state.visits > 5:
        state.server_status = "HIGH LOAD"
        state.status_color = "#ff9900" # Orange
    
    if state.visits > 10:
        state.server_status = "CRITICAL OVERLOAD"
        state.status_color = "#ff0000" # Red

def reset_system():
    state.visits = 0
    state.server_status = "ONLINE"
    state.status_color = "#00ff00"

# --- 3. THE UI (Weaves itself) ---
with app.root:
    # Header
    app.Text("⚡ LoomUI Real-Time Demo", size="24px", weight="bold")
    
    # The "Magic" Binding: $variable automatically binds to state
    with app.Row():
        app.Text("Server Status: ")
        # We bind the 'color' property to the state variable too!
        app.Text("$server_status", color="$status_color", weight="bold")

    # Metrics Display
    with app.Card():
        app.Text("Total Requests", size="14px", color="#666")
        app.Text("$visits", size="36px") # Updates instantly

    # Controls
    with app.Row():
        app.Button("💥 Simulate Traffic", on_click=simulate_traffic, variant="primary")
        app.Button("↺ Reset System", on_click=reset_system, variant="secondary")

# Run the app
if __name__ == "__main__":
    app.run()
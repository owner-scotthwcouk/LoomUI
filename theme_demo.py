from loom import LoomApp, state

# --- THE UNIQUE PART: CUSTOM THEME ---
cyberpunk_theme = {
    "background": "#000000",
    "surface": "#121212",
    "text": "#00ff41",        # Hacker Green
    "primary": "#d900ff",     # Neon Purple
    "primary_hover": "#b200d1",
    "border": "#333333",
    "font": "Courier New, monospace", # Retro font
    "radius": "0px"           # Sharp edges
}

app = LoomApp(theme=cyberpunk_theme)

with app.root:
    app.Text("# SYSTEM STATUS: ONLINE")
    app.Text("Welcome to the mainframe.")
    
    with app.Row():
        app.Button("INITIATE PROTOCOL", on_click=lambda: print("Hacking..."))
        app.Input(value="Enter Access Code")
    
    app.Text("# SERVER LOAD")
    app.Chart(
        type="line", 
        labels=["00:00", "00:01", "00:02", "00:03"], 
        data=[12, 45, 89, 23]
    )

if __name__ == "__main__":
    app.run()
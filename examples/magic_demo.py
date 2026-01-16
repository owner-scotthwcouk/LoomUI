from loom import LoomApp, expose

app = LoomApp()

# --- THE MAGIC ---
# You don't write UI code. You just write logic.
@expose
def calculate_bmi(weight_kg: int, height_m: float):
    if height_m == 0: return 0
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 2)

@expose
def greet_user(name: str, times: int):
    return f"Hello {name}! " * times

# --- LAYOUT ---
with app.root:
    app.Text("LoomUI Auto-Generator")
    
    # We just add the function objects directly!
    # (The decorator turned them into UI Components)
    app.root.children.append(calculate_bmi)
    app.root.children.append(greet_user)

if __name__ == "__main__":
    app.run()
# LoomUI: The Thread-Safe Interface That Weaves Itself

[![PyPI version](https://badge.fury.io/py/loomui.svg)](https://badge.fury.io/py/loomui)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LoomUI** is a next-generation Python framework designed to bridge the gap between simple scripts and complex dashboards. Unlike other libraries that require callbacks, manual state management, or reactive graph definitions, LoomUI uses **Invisible State Monitoring** to update your UI automatically.

Write standard Python. Get a real-time SPA (Single Page Application).

---

## 🚀 Key Features

* **🪄 Function-is-the-Interface:** Use the `@expose` decorator to instantly turn any Python function into a web form with inputs and validation.
* **🧠 Invisible State:** No `session_state["key"]`. No callbacks. Just modify `state.x = 5`, and the UI updates.
* **⚡ WebSocket Powered:** Built on **FastAPI** and **Uvicorn** for bi-directional, real-time communication.
* **🎨 Theme Engine:** One-line CSS variable theming. Cyberpunk? Dark mode? Corporate? Just pass a dict.
* **📊 Integrated Charts:** Full **Chart.js** support right out of the box.

---

## 📦 Installation

```bash
pip install loomui
```
---

## ⚡ Quick Start: The "Magic" Mode
The fastest way to build a tool. LoomUI inspects your function signatures and generates the UI.

```Python

from loom import LoomApp, expose

app = LoomApp()

@expose
def calculate_roi(investment: float, rate: float, years: int):
    """Calculates return on investment instantly."""
    return investment * ((1 + rate) ** years)

if __name__ == "__main__":
    app.run()
```
---
## 🛠️ Advanced: The "Layout" Mode
For full control over dashboards, charts, and state.

```Python

from loom import LoomApp, state

# 1. Define Theme
dark_theme = {"background": "#111", "text": "#0f0", "primary": "#d0f"}
app = LoomApp(theme=dark_theme)

# 2. Define State
state.count = 0

# 3. Define Logic
def increment():
    state.count += 1

# 4. Build Layout
with app.root:
    app.Text("# System Monitor")
    
    with app.Row():
        app.Button("INCREASE LOAD", on_click=increment)
        app.Text("Current Load: $count") # '$' binds automatically to state
    
    app.Chart(
        type="line",
        labels=["00:00", "00:01", "00:02"],
        data=[10, 25, 60]
    )

if __name__ == "__main__":
    app.run()
```
---

## 🎨 Theming
LoomUI supports full customization via a simple dictionary:

```Python

theme = {
    "background": "#ffffff",
    "surface": "#f4f4f9", 
    "text": "#333333",
    "primary": "#6200ea",
    "radius": "12px"
}
app = LoomApp(theme=theme)
```
---

## 📄 License
MIT License. Free to use for personal and commercial projects.


---
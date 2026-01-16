# Loom UI 🧶

**Build modern, real-time Python dashboards without writing a single line of JavaScript.**

Loom UI is a lightweight, zero-dependency (almost) library that lets you create interactive single-page applications (SPAs), admin panels, and data dashboards purely in Python. It handles the frontend rendering, state management, and WebSocket communication for you.

## 🚀 Features
* **Zero JavaScript Required:** Write Python, get a React-like UI.
* **Real-Time by Default:** Built on WebSockets; UI updates instantly when Python state changes.
* **Reactive State:** Just change `state.value = 10` and the UI updates automatically.
* **Enterprise Components:** Includes Tables, Charts, Sidebars, Modals, Metrics, and Forms out of the box.
* **Zero-Flicker Engine:** Smart DOM patching ensures smooth updates, even for high-frequency data.

## 📦 Installation

```bash
pip install loom-ui
```

## ⚡ Quick Start
Create a file app.py:

```Python
from loom import LoomApp, state
import time, threading

app = LoomApp()

# 1. Define State
state.counter = 0

# 2. Background Task (Optional)
def tick():
    while True:
        state.counter += 1
        time.sleep(1)

threading.Thread(target=tick, daemon=True).start()

# 3. Build UI
with app.Navbar(title="My Dashboard"):
    app.Text("v0.1.0")

with app.Card(title="Live Counter"):
    # The "$" tells Loom to bind to the state variable
    app.Metric(label="Seconds Running", value="$counter", color="blue")
    app.ProgressBar(value_var="counter", color="blue")

if __name__ == "__main__":
    app.run()
```
## Run it:

```Bash

python app.py
```

## 📚 Documentation
Full documentation is available in DOCS.md.

## 📄 License
MIT License
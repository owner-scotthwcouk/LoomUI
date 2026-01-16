# 📚 Loom UI Documentation (v0.1.0)
Loom UI is a reactive Python library for building modern single-page applications (SPAs), admin panels, and real-time dashboards. It bridges Python state directly to the browser DOM via WebSockets, allowing you to create interactive UIs without writing a single line of JavaScript.

## 📋 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Concepts](#core-concepts)
    * [The App Tree](#the-app-tree)
    * [State Management](#state-management)
    * [The Zero-Flicker Engine](#the-zero-flicker-engine)
3. [Component Reference](#component-reference)
    * [Layout Components](#layout-components)
    * [Input & Control Components](#input--control-components)
    * [Data Display Components](#data-display-components)
4. [Advanced Patterns](#advanced-patterns)
    * [Routing (Single Page Apps)](#routing)
    * [Background Tasks](#background-tasks)
5. [Deployment](#deployment)

## Installation & Setup
**Requirements**
Python: 3.7 or higher

**Dependencies:**
 fastapi, uvicorn, websockets (installed automatically)

**Installation**
```Bash

pip install loom-ui
```
**Quick Start: "Hello World"**
Create a file named app.py:

```Python

from loom import LoomApp, state

app = LoomApp()

# 1. Define State
state.counter = 0

# 2. Define Action
def increment():
    state.counter += 1

# 3. Build UI
with app.Card(title="My First App"):
    app.Text("Current Count: $counter", size="xl")
    app.Button("Click Me", on_click=increment)

if __name__ == "__main__":
    app.run()
```
**Run the server:**

```Bash

python app.py
```
Open your browser to http://127.0.0.1:8088.

[back to the top](#-loom-ui-documentation-v010)
## Core Concepts
### The App Tree
Loom uses Python Context Managers (with statements) to define the hierarchy of your user interface. This ensures your code structure visually matches the resulting UI structure.

**Example:**

```Python

with app.Row():                  # Parent Container
    with app.Card():             # Child Container
        app.Text("I am inside")  # Leaf Widget
```
### State Management
Loom relies on a single global state object. The frontend is a reflection of this state.

Define: simply assign variables to state (e.g., `state.username = "Alice"`).

Bind: Use the $ prefix in component strings to bind them to a variable.

`app.Text("Hello $username")` renders as `"Hello Alice"`.

Update: Modify the variable in Python (`state.username = "Bob"`). The UI updates instantly via WebSocket.

Batch Updates
When updating multiple variables rapidly (e.g., in a background loop), use batch_update to group changes into a single network message. This prevents flickering.

```Python

with state.batch_update():
    state.cpu_load = 45
    state.memory = 60
    state.disk = 12
```
### The Zero-Flicker Engine
In v0.1.0, Loom introduces a Virtual DOM Patcher.

Instead of replacing the entire HTML body on every update, Loom sends a JSON description of the UI.

The client-side JavaScript compares this JSON with the existing page.

It only updates the elements that changed (e.g., changing text inside a <span> or appending a row to a <table>).

Result: Inputs don't lose focus, scroll position is maintained, and charts animate smoothly.

[back to the top](#-loom-ui-documentation-v010)
## Component Reference
### Layout Components
<div style="border: 1px solid black; padding: 10px;">
`app.Navbar(title)`
A fixed top navigation bar.

+ `title (str):` The application name displayed on the left.
+ Usage: Place global actions (Logout, Profile) inside.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Sidebar()`
A fixed left-hand vertical menu.

+ Usage: Best used as the first child of an app.Row(). It automatically handles full height styling.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Page(name)`
A logical container for routing.

+ `name (str):` Unique identifier for the page.
+ Behavior: The content inside is hidden unless state.active_page matches name.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Row()`
A horizontal container (Flexbox Row). Children are placed side-by-side with gaps.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Column()`
A vertical container (Flexbox Column). Children are stacked vertically.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Card(title="")`
A polished container with a white background, shadow, and rounded corners.

+ `title (str, optional):` If provided, adds a header text to the card.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Modal(open_var)`
A popup dialog overlay.

+ `open_var (str):` The name of the boolean state variable controlling visibility (e.g., `"show_dialog"`).
</div>

### Input & Control Components
<div style="border: 1px solid black; padding: 10px;">
`app.Button(label, on_click=None, variant="primary")`
A clickable button.

+ `label (str): Button text`.
+ `on_click (callable)`: Python function to run when clicked.
+ `variant (str)`: Controls styling.

    + `"primary"` (Indigo/Blue)

    + `"secondary"` (Gray/Light)

    + `"danger"` (Red)

    + `"active"` (Highlighted state, useful for Sidebar tabs)
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Input(value_var, placeholder="...")`
A text input field.

+ `value_var (str)`: State variable to bind to (Two-way binding).
+ `placeholder (str)`: Hint text when empty.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Select(value_var, options=[])`
A dropdown menu.

+ `value_var (str)`: State variable to bind to.
+ `options (list[str])`: List of strings to display as options.
</div>

### Data Display Components
<div style="border: 1px solid black; padding: 10px;">
`app.Text(content, size="base", color="inherit")`
Displays text.

+ `content (str)`: Text to display. Supports variable binding (e.g., `"$user"`).
+ `size (str)`: "sm", "base", "lg", "xl".
+ `color (str)`: Tailwind color class (e.g., "red", "gray") or hex code.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Metric(label, value, trend=None, color="blue")`
A large Key Performance Indicator (KPI) display.

+ `label (str)`: Top label (e.g., "Total Revenue").
+ `value (str/int)`: The main number.
+ `trend (str, optional)`: Small text below value (e.g., "▲ 12%").
+ `color (str)`: Color of the main value text.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Table(data_var, headers=[])`
Renders a data table from a list of lists.

+ `data_var (str)`: Name of the state variable containing the data rows (e.g., [[1, "Alice"], [2, "Bob"]]).
+ `headers (list[str])`: List of column names.
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.Chart(data_var, title, color)`
Renders a responsive line chart using Chart.js.

+ `data_var (str)`: Name of the state variable containing a list of numbers.
+ `title (str)`: Label for the dataset.
+ `color (str)`: Color of the line and fill area (e.g., "rgb(75, 192, 192)").
</div>

<div style="border: 1px solid black; padding: 10px;">
`app.ProgressBar(value_var, color="blue")`
A horizontal progress bar.

+ `value_var (str)`: Name of the state variable (0-100).
+ `color (str)`: Color of the bar.
</div>

[back to the top](#-loom-ui-documentation-v010)
## Advanced Patterns
### Routing
To create a Single Page Application with multiple "pages", combine app.Sidebar buttons with app.Page containers.

```Python

# 1. State for Routing
state.current_page = "Home"

# 2. Handler
def go_to(page):
    def _handler():
        state.current_page = page
    return _handler

# 3. UI
with app.Row():
    with app.Sidebar():
        app.Button("Home", on_click=go_to("Home"))
        app.Button("Settings", on_click=go_to("Settings"))
    
    with app.Column():
        with app.Page("Home"):
            app.Text("Welcome Home")
        
        with app.Page("Settings"):
            app.Text("System Configuration")
```
### Background Tasks
Loom runs on asyncio (via FastAPI), but you can use standard Python threading for background logic (like reading sensors or querying databases).

Always use `state.batch_update()` inside threads to keep the UI smooth.

```Python

def sensor_loop():
    while True:
        data = read_sensor()
        with state.batch_update():
            state.temp = data['temp']
            state.humidity = data['hum']
        time.sleep(1)

threading.Thread(target=sensor_loop, daemon=True).start()
```

[back to the top](#-loom-ui-documentation-v010)
## Deployment
Because Loom is built on FastAPI and Uvicorn, it is production-ready.

**Running in Production**
Do not use `app.run()` in production. Instead, expose the internal FastAPI server object and run it with a WSGI/ASGI server.

File: main.py

```Python

from loom import LoomApp
app_instance = LoomApp()
# ... define UI ...
server = app_instance.app # Expose the FastAPI object
```
**Command Line:**

```Bash

uvicorn main:server --host 0.0.0.0 --port 80 --workers 1
```
***Note: Since Loom relies on a single global state object, it currently supports one active state instance. Multiple workers will result in separate states for separate users. For a shared global dashboard state across multiple users, use a single worker.***
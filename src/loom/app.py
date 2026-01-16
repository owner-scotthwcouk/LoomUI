# D:\Dev\Loom-UI\src\loom\app.py
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json

# Import components and state cleanly
from .components import Column, Row, Text, Button, Input, Chart, Component, Card
from .state import current_context, state, component_registry

class LoomApp:
    def __init__(self):
        self.app = FastAPI()
        # The root is a Column that holds everything
        self.root = Column()
        
        # Setup the "Global" context to start at the root
        current_context.append(self.root)

        self._setup_routes()

    # --- HELPER TO ADD COMPONENTS ---
    def add(self, component):
        """Adds a component to the currently active container."""
        if current_context:
            parent = current_context[-1]
            # Ensure we don't accidentally add to self if something went wrong
            if parent != component:
                parent.add(component)
        else:
            self.root.add(component)
            
    # --- SHORTCUTS ---
    def Text(self, *args, **kwargs): self.add(Text(*args, **kwargs))
    def Button(self, *args, **kwargs): self.add(Button(*args, **kwargs))
    def Input(self, *args, **kwargs): self.add(Input(*args, **kwargs))
    def Chart(self, *args, **kwargs): self.add(Chart(*args, **kwargs))
    
    # Context managers return the instance, they don't add themselves automatically yet
    def Row(self, *args, **kwargs): 
        r = Row(*args, **kwargs)
        self.add(r)
        return r

    def Column(self, *args, **kwargs): 
        c = Column(*args, **kwargs)
        self.add(c)
        return c

    def Card(self, *args, **kwargs): 
        c = Card(*args, **kwargs)
        self.add(c)
        return c

    # --- SERVER LOGIC ---
    def _setup_routes(self):
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LoomUI</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                const ws = new WebSocket("ws://localhost:8000/ws");
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    document.getElementById("app").innerHTML = ""; 
                    render(data, document.getElementById("app"));
                };

                function render(node, parent) {
                    let el;
                    if (node.type === "Text") {
                        el = document.createElement("div");
                        // Handle Markdown Headers
                        if (node.content.startsWith("# ")) {
                             el = document.createElement("h1");
                             el.innerText = node.content.replace("# ", "");
                             el.className = "text-3xl font-bold mb-4";
                        } else if (node.content.startsWith("## ")) {
                             el = document.createElement("h2");
                             el.innerText = node.content.replace("## ", "");
                             el.className = "text-2xl font-bold mb-2";
                        } else if (node.content === "---") {
                             el = document.createElement("hr");
                             el.className = "my-4 border-gray-300";
                        } else {
                             el.innerText = node.content;
                             el.className = "text-gray-700";
                        }
                    } 
                    else if (node.type === "Button") {
                        el = document.createElement("button");
                        el.innerText = node.label;
                        el.className = "px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition mr-2";
                        el.onclick = () => ws.send(JSON.stringify({type: "click", id: node.id}));
                    }
                    else if (node.type === "Row") {
                        el = document.createElement("div");
                        el.className = "flex flex-row gap-4 items-center mb-2";
                        if (node.children) node.children.forEach(c => render(c, el));
                    }
                    else if (node.type === "Column" || node.type === "Card") { 
                        el = document.createElement("div");
                        if (node.type === "Card") el.className = "p-6 bg-white shadow-lg rounded-xl border border-gray-100 mb-4";
                        else el.className = "flex flex-col gap-2";
                        if (node.children) node.children.forEach(c => render(c, el));
                    }
                    
                    if (el) parent.appendChild(el);
                }
            </script>
        </head>
        <body class="bg-gray-50 p-10">
            <div id="app" class="max-w-2xl mx-auto"></div>
        </body>
        </html>
        """

        @self.app.get("/")
        async def get():
            return HTMLResponse(html_template)

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            # Send initial UI
            await websocket.send_json(self.root.to_dict())
            
            while True:
                try:
                    data = await websocket.receive_json()
                    if data["type"] == "click":
                        # CRITICAL FIX: Find the component and run its function
                        comp_id = data.get("id")
                        if comp_id in component_registry:
                            comp = component_registry[comp_id]
                            if hasattr(comp, 'on_click') and comp.on_click:
                                print(f"Executing click for {comp.label}")
                                comp.on_click()
                        
                        # Re-render UI to show state changes
                        await websocket.send_json(self.root.to_dict())
                except Exception as e:
                    print(f"WebSocket Error: {e}")
                    break

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000)
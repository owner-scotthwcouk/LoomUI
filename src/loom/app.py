import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import json
from .components import Column, Row, Text, Button, Input, Chart
from .state import state

# --- DEFAULT THEME ---
DEFAULT_THEME = {
    "background": "#f4f4f9",
    "surface": "#ffffff",
    "text": "#1f2937",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "border": "#e5e7eb",
    "font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    "radius": "8px"
}

class LoomApp:
    def __init__(self, theme=None):
        self.app = FastAPI()
        self.root = Column() 
        self.component_map = {}
        self.active_socket = None
        
        # Merge user theme with default
        self.theme = DEFAULT_THEME.copy()
        if theme:
            self.theme.update(theme)
        
        # Expose components
        self.Column = Column
        self.Row = Row
        self.Text = Text
        self.Button = Button
        self.Input = Input
        self.Chart = Chart
        
        state._app_ref = self
        
        self.app.get("/")(self.get_html)
        self.app.websocket("/ws")(self.websocket_endpoint)

    def run(self, host="127.0.0.1", port=8000):
        uvicorn.run(self.app, host=host, port=port)

    def _register_all(self, comp):
        self.component_map[comp.id] = comp
        if hasattr(comp, 'children'):
            for child in comp.children:
                self._register_all(child)

    def push_update(self, component_id, new_value):
        if self.active_socket:
            payload = {"action": "update", "id": component_id, "value": str(new_value)}
            asyncio.create_task(self.active_socket.send_text(json.dumps(payload)))

    async def get_html(self):
        self._register_all(self.root)
        initial_tree = json.dumps(self.root.to_json())
        
        # Inject CSS Variables based on Python Theme Dict
        css_vars = f"""
            --bg-color: {self.theme['background']};
            --surface-color: {self.theme['surface']};
            --text-color: {self.theme['text']};
            --primary-color: {self.theme['primary']};
            --primary-hover: {self.theme['primary_hover']};
            --border-color: {self.theme['border']};
            --font-family: {self.theme['font']};
            --radius: {self.theme['radius']};
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Loom App</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                :root {{
                    {css_vars}
                }}
                
                body {{ 
                    font-family: var(--font-family); 
                    padding: 2rem; 
                    background: var(--bg-color); 
                    color: var(--text-color);
                    transition: background 0.3s, color 0.3s;
                }}
                
                #root {{ 
                    max-width: 900px; 
                    margin: 0 auto; 
                    background: var(--surface-color); 
                    padding: 40px; 
                    border-radius: 16px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
                }}
                
                .Column {{ display: flex; flex-direction: column; gap: 20px; }}
                .Row {{ display: flex; flex-direction: row; gap: 20px; align-items: center; flex-wrap: wrap; }}
                
                button {{ 
                    padding: 12px 24px; 
                    cursor: pointer; 
                    background: var(--primary-color); 
                    color: white; 
                    border: none; 
                    border-radius: var(--radius); 
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    transition: all 0.2s ease;
                }}
                button:hover {{ background: var(--primary-hover); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                button:active {{ transform: translateY(0); }}

                input {{
                    padding: 10px 16px;
                    border: 2px solid var(--border-color);
                    border-radius: var(--radius);
                    font-size: 15px;
                    background: transparent;
                    color: var(--text-color);
                    outline: none;
                    transition: border-color 0.2s;
                }}
                input:focus {{ border-color: var(--primary-color); }}
                
                div {{ font-size: 16px; line-height: 1.6; }}
                
                h1, h2, h3 {{ margin: 0; font-weight: 700; color: var(--text-color); }}
                
                canvas {{ max-width: 100%; }}
            </style>
        </head>
        <body>
            <div id="root"></div>
            <script>
                const rootData = {initial_tree};
                const ws = new WebSocket("ws://" + window.location.host + "/ws");

                function render(comp, parent) {{
                    let el;
                    if (comp.type === "Column" || comp.type === "Row") {{
                        el = document.createElement("div");
                        el.className = comp.type;
                    }} else if (comp.type === "Text") {{
                        el = document.createElement("div");
                        // Rudimentary header detection
                        if (comp.value.startsWith("# ")) {{
                            const h = document.createElement("h2");
                            h.innerText = comp.value.replace("# ", "");
                            el = h;
                        }} else {{
                            el.innerText = comp.value;
                        }}
                    }} else if (comp.type === "Button") {{
                        el = document.createElement("button");
                        el.innerText = comp.label;
                        el.onclick = () => ws.send(JSON.stringify({{event: "click", id: comp.id}}));
                    }} else if (comp.type === "Input") {{
                        el = document.createElement("input");
                        el.value = comp.value;
                        el.oninput = (e) => {{
                            ws.send(JSON.stringify({{
                                event: "input", 
                                id: comp.id, 
                                value: e.target.value
                            }}));
                        }};
                    }} else if (comp.type === "Chart") {{
                        const container = document.createElement("div");
                        container.style.width = "100%"; 
                        const canvas = document.createElement("canvas");
                        container.appendChild(canvas);
                        el = container;
                        
                        requestAnimationFrame(() => {{
                            // Auto-color based on CSS variables is hard in JS, so we use defaults for now
                            new Chart(canvas, {{
                                type: comp.chartType,
                                data: {{
                                    labels: comp.labels,
                                    datasets: [{{
                                        label: 'Data',
                                        data: comp.data,
                                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                                        borderColor: 'rgba(54, 162, 235, 1)',
                                        borderWidth: 1
                                    }}]
                                }},
                                options: {{ responsive: true }}
                            }});
                        }});
                    }}
                    
                    el.id = comp.id;
                    parent.appendChild(el);
                    if (comp.children) comp.children.forEach(child => render(child, el));
                }}

                render(rootData, document.getElementById("root"));

                ws.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    if (data.action === "update") {{
                        const el = document.getElementById(data.id);
                        if (el) {{
                            if (el.tagName === "INPUT") {{
                                if (document.activeElement !== el) el.value = data.value;
                            }} else {{
                                el.innerText = data.value;
                            }}
                        }}
                    }}
                }};
            </script>
        </body>
        </html>
        """
        return HTMLResponse(html)

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        self.active_socket = websocket
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                if msg['event'] == 'click':
                    comp = self.component_map.get(msg['id'])
                    if comp and hasattr(comp, 'on_click'): comp.on_click()
                elif msg['event'] == 'input':
                    comp = self.component_map.get(msg['id'])
                    if comp and hasattr(comp, 'handle_input'): comp.handle_input(msg['value'])
        except Exception as e:
            print(f"WebSocket disconnected: {e}")
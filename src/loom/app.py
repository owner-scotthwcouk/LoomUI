# src/loom/app.py
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
from .components import *
from .state import current_context, state, component_registry

class LoomApp:
    def __init__(self):
        self.app = FastAPI()
        self.root = Column()
        current_context.append(self.root)
        self.active_connections = set()
        self.loop = None
        state.add_listener(self._on_state_change)
        self._setup_routes()

    def _on_state_change(self):
        if not self.loop or not self.active_connections: return
        try:
            if asyncio.get_running_loop() is self.loop: self.loop.create_task(self.broadcast()); return
        except: pass
        asyncio.run_coroutine_threadsafe(self.broadcast(), self.loop)

    async def broadcast(self):
        if not self.active_connections: return
        try: ui_data = self.root.to_dict()
        except: return
        dead = set()
        for ws in self.active_connections:
            try: await ws.send_json(ui_data)
            except: dead.add(ws)
        for ws in dead: self.active_connections.remove(ws)

    def add(self, c):
        if current_context: current_context[-1].add(c)
        else: self.root.add(c)
    
    # Shortcuts
    def Navbar(self, *a, **k): n = Navbar(*a, **k); self.add(n); return n
    def Sidebar(self, *a, **k): s = Sidebar(*a, **k); self.add(s); return s
    def Page(self, *a, **k): p = Page(*a, **k); self.add(p); return p
    def Row(self, *a, **k): r = Row(*a, **k); self.add(r); return r
    def Column(self, *a, **k): c = Column(*a, **k); self.add(c); return c
    def Card(self, *a, **k): c = Card(*a, **k); self.add(c); return c
    def Modal(self, *a, **k): m = Modal(*a, **k); self.add(m); return m
    def Text(self, *a, **k): self.add(Text(*a, **k))
    def Button(self, *a, **k): self.add(Button(*a, **k))
    def Input(self, *a, **k): self.add(Input(*a, **k))
    def Select(self, *a, **k): self.add(Select(*a, **k)) # NEW
    def Metric(self, *a, **k): self.add(Metric(*a, **k))
    def Chart(self, *a, **k): self.add(Chart(*a, **k))
    def Table(self, *a, **k): self.add(Table(*a, **k))
    def ProgressBar(self, *a, **k): self.add(ProgressBar(*a, **k))

    def _setup_routes(self):
        @self.app.on_event("startup")
        async def startup(): self.loop = asyncio.get_running_loop()
        html_template = """
        <!DOCTYPE html><html><head><title>Loom Admin</title>
        <script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>body{font-family:'Inter',sans-serif;background-color:#f3f4f6}.custom-scroll::-webkit-scrollbar{width:5px;height:5px}.custom-scroll::-webkit-scrollbar-thumb{background:#94a3b8;border-radius:4px}</style>
        <script>
        const ws = new WebSocket("ws://127.0.0.1:8088/ws"); const charts = {};
        ws.onmessage = function(event) { patch(JSON.parse(event.data), document.getElementById("app")); };
        function patch(node, parent) {
            if (node.type === "Hidden") { const e = document.getElementById(node.id); if(e) e.style.display='none'; return; }
            let el = document.getElementById(node.id);
            if (!el) { el = createElement(node); if(el) parent.appendChild(el); } 
            else { el.style.display = ''; updateElement(el, node); }
            if (!el) return;
            let container = el;
            if (node.id && document.getElementById(node.id + "_content")) container = document.getElementById(node.id + "_content");
            if (node.id && document.getElementById(node.id + "_right")) container = document.getElementById(node.id + "_right");
            if (node.children) node.children.forEach(c => patch(c, container));
        }
        function updateElement(el, node) {
            if (node.type==="Text" && el.innerText!==node.content) el.innerText=node.content;
            if (node.type==="Button") {
                 if(el.innerText.trim()!==node.label) el.innerText=node.label;
                 if(node.variant==='active' && !el.className.includes('bg-indigo')) el.className="w-full text-left px-4 py-3 rounded-lg bg-indigo-600 text-white shadow-md transition text-sm font-medium flex items-center";
                 if(node.variant!=='active' && el.className.includes('bg-indigo')) el.className="w-full text-left px-4 py-3 rounded-lg hover:bg-slate-800 transition text-sm font-medium flex items-center text-gray-300";
            }
            if (node.type==="Metric") el.querySelector(".metric-value").innerText=node.value;
            if (node.type==="ProgressBar") el.querySelector("div").style.width=node.value+"%";
            if (node.type==="Input" && document.activeElement!==el) el.value=node.value;
            if (node.type==="Select" && document.activeElement!==el) el.value=node.value;
            if (node.type==="Chart" && charts[node.id]) { charts[node.id].data.datasets[0].data=node.data; charts[node.id].update('none'); }
            if (node.type==="Table") {
                const tbody = el.querySelector("tbody");
                const newHtml = node.rows.map(row => `<tr>${(Array.isArray(row)?row:Object.values(row)).map(c => `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${c}</td>`).join('')}</tr>`).join('');
                if (tbody.innerHTML !== newHtml) tbody.innerHTML = newHtml;
            }
        }
        function createElement(node) {
            let el;
            if (node.type==="Navbar") { el=document.createElement("nav"); el.id=node.id; el.className="w-full bg-white border-b border-gray-200 text-slate-800 px-6 py-3 flex items-center shadow-sm fixed top-0 left-0 z-50 h-16"; el.innerHTML=`<h1 class='text-lg font-bold text-indigo-600'><i class="fa-solid fa-cube mr-2"></i>${node.title}</h1>`; const r=document.createElement("div"); r.className="ml-auto flex gap-4 items-center"; r.id=node.id+"_right"; el.appendChild(r); document.body.style.paddingTop="4rem"; }
            else if (node.type==="Sidebar") { el=document.createElement("aside"); el.id=node.id; el.className="w-64 bg-slate-900 text-gray-300 h-screen fixed left-0 top-16 overflow-y-auto p-4 flex flex-col gap-2 border-r border-slate-800 z-40"; }
            else if (node.type==="Page") { el=document.createElement("div"); el.id=node.id; el.className="flex flex-col gap-6 w-full animate-fade-in"; }
            else if (node.type==="Row") { el=document.createElement("div"); el.id=node.id; el.className="flex flex-row gap-6 w-full items-start"; if(node.children && node.children.some(c=>c.type==="Sidebar")){ el.className="flex flex-row w-full"; const w=document.createElement("div"); w.className="flex-1 ml-64 p-8 flex flex-col gap-6"; w.id=node.id+"_content"; el.appendChild(w); } }
            else if (node.type==="Column") { el=document.createElement("div"); el.id=node.id; el.className="flex flex-col gap-4 w-full"; }
            else if (node.type==="Card") { el=document.createElement("div"); el.id=node.id; el.className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 w-full"; if(node.title) el.innerHTML=`<div class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">${node.title}</div>`; }
            else if (node.type==="Metric") { el=document.createElement("div"); el.id=node.id; el.className="flex flex-col"; el.innerHTML=`<span class="text-sm text-gray-500">${node.label}</span><span class="text-3xl font-bold text-${node.color}-600 mt-1 metric-value">${node.value}</span>`+(node.trend?`<span class="text-xs text-green-500 mt-1">▲ ${node.trend}</span>`:''); }
            else if (node.type==="Button") { el=document.createElement("button"); el.id=node.id; const c=node.variant==='danger'?'bg-red-500 hover:bg-red-600':(node.variant==='secondary'?'bg-gray-200 text-gray-800 hover:bg-gray-300':'bg-indigo-600 hover:bg-indigo-700 text-white'); el.className=`px-4 py-2 ${c} rounded-lg shadow-sm transition transform active:scale-95 font-medium text-sm`; el.innerText=node.label; el.onclick=()=>ws.send(JSON.stringify({type:"click",id:node.id})); }
            else if (node.type==="Input") { el=document.createElement("input"); el.id=node.id; el.className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"; el.placeholder=node.placeholder; el.oninput=(e)=>ws.send(JSON.stringify({type:"input",id:node.id,value:e.target.value})); }
            else if (node.type==="Select") { el=document.createElement("select"); el.id=node.id; el.className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none bg-white"; el.onchange=(e)=>ws.send(JSON.stringify({type:"input",id:node.id,value:e.target.value})); node.options.forEach(opt=>{const o=document.createElement("option"); o.value=opt; o.innerText=opt; if(opt===node.value) o.selected=true; el.appendChild(o)}); }
            else if (node.type==="Table") { el=document.createElement("div"); el.id=node.id; el.className="overflow-x-auto custom-scroll border rounded-lg"; el.innerHTML=`<table class="min-w-full divide-y divide-gray-200"><thead class="bg-gray-50"><tr>${node.headers.map(h=>`<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">${h}</th>`).join('')}</tr></thead><tbody class="bg-white divide-y divide-gray-200">${node.rows.map(row=>`<tr>${(Array.isArray(row)?row:Object.values(row)).map(c=>`<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`; }
            else if (node.type==="Chart") { const d=document.createElement("div"); d.className="h-64 w-full relative"; d.id=node.id; const c=document.createElement("canvas"); d.appendChild(c); el=d; setTimeout(()=>{charts[node.id]=new Chart(c,{type:'line',data:{labels:node.labels,datasets:[{label:node.title,data:node.data,borderColor:node.color,tension:0.4,fill:true,backgroundColor:node.color.replace('rgb','rgba').replace(')',',0.1)')}]},options:{maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false},y:{grid:{borderDash:[5,5]}}}}})},0); }
            else if (node.type==="Text") { el=document.createElement("div"); el.id=node.id; el.className=node.size==="xl"?"text-2xl font-bold":node.size==="lg"?"text-lg font-semibold":"text-base text-gray-600"; el.innerText=node.content; }
            else if (node.type==="ProgressBar") { el=document.createElement("div"); el.id=node.id; el.className="w-full bg-gray-200 rounded-full h-2"; el.innerHTML=`<div class="bg-${node.color}-500 h-2 rounded-full" style="width:${node.value}%"></div>`; }
            return el;
        }
        </script></head><body><div id="app"></div></body></html>
        """
        @self.app.get("/")
        async def get(): return HTMLResponse(html_template)
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.add(websocket)
            await websocket.send_json(self.root.to_dict())
            try:
                while True:
                    data = await websocket.receive_json()
                    if data["type"] == "click":
                         if data["id"] in component_registry:
                             f = component_registry[data["id"]].on_click; 
                             if f: f()
                    elif data["type"] == "input":
                         if data["id"] in component_registry:
                             setattr(state, component_registry[data["id"]].value_var, data["value"])
            except: pass
            finally: 
                if websocket in self.active_connections: self.active_connections.remove(websocket)

    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=8088)
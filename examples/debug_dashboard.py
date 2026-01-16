from loom import LoomApp, state
import sys

print("--- Initializing App ---")
app = LoomApp()

state.count = 0
state.message = "Debug Mode"

def increment():
    state.count += 1
    state.message = f"Count: {state.count}"

print("--- Building Layout ---")
# 1. Enter the Main Window
with app.root:
    print("   > Entered app.root")
    
    # 2. Add Components
    t1 = app.Text("LoomUI Debugger")
    print(f"   > Created Text: {t1.id}")
    
    with app.Row():
        print("      > Entered Row")
        b1 = app.Button("Click Me", on_click=increment)
        print(f"      > Created Button: {b1.id}")
        
    t2 = app.Text("$message")
    print(f"   > Created Dynamic Text: {t2.id}")

print("--- Checking Tree ---")
child_count = len(app.root.children)
print(f"App Root has {child_count} children.")

if child_count == 0:
    print("❌ ERROR: The components were not attached! Check indentation.")
else:
    print("✅ SUCCESS: Python sees the components. If browser is blank, check F12 Console.")

if __name__ == "__main__":
    app.run()
    
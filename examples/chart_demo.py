from loom import LoomApp

app = LoomApp()

with app.root:
    app.Text("Quarterly Sales Dashboard")
    
    # A Row of Charts
    with app.Row():
        with app.Column():
            app.Text("Revenue (Bar)")
            app.Chart(
                type="bar", 
                labels=["Q1", "Q2", "Q3", "Q4"], 
                data=[12000, 19000, 3000, 5000]
            )
            
        with app.Column():
            app.Text("Growth (Line)")
            app.Chart(
                type="line", 
                labels=["Jan", "Feb", "Mar", "Apr"], 
                data=[10, 25, 40, 35]
            )

if __name__ == "__main__":
    app.run()
import tkinter as tk
from tkinter import ttk, messagebox
import math

class TouristOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Tourist Travel Optimizer")
        self.root.geometry("800x600")
        
        # Sample tourist attractions data
        
        self.attractions = [
            {"name": "Taj Mahal", "cost": 15, "time": 4, "rating": 9.8},
            {"name": "Red Fort", "cost": 5, "time": 2.5, "rating": 8.9},
            {"name": "India Gate", "cost": 0, "time": 1.5, "rating": 8.4},
            {"name": "Qutub Minar", "cost": 3, "time": 2, "rating": 8.6},
            {"name": "Lotus Temple", "cost": 0, "time": 1, "rating": 8.7},
            {"name": "Amber Fort", "cost": 10, "time": 3.5, "rating": 9.1},
            {"name": "Gateway of India", "cost": 0, "time": 1, "rating": 8.2},
            {"name": "Hawa Mahal", "cost": 2, "time": 1.5, "rating": 8.5}
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Tourist Travel Optimizer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Travel Constraints", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Budget input
        ttk.Label(input_frame, text="Budget ($):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.budget_var = tk.StringVar(value="100")
        budget_entry = ttk.Entry(input_frame, textvariable=self.budget_var, width=15)
        budget_entry.grid(row=0, column=1, sticky=tk.W)
        
        # Time input
        ttk.Label(input_frame, text="Available Time (hours):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.time_var = tk.StringVar(value="12")
        time_entry = ttk.Entry(input_frame, textvariable=self.time_var, width=15)
        time_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Optimize button
        optimize_btn = ttk.Button(input_frame, text="Optimize Itinerary", command=self.optimize)
        optimize_btn.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Available Attractions", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Attractions treeview
        self.attractions_tree = ttk.Treeview(results_frame, columns=("Cost", "Time", "Rating", "Value/Cost"), show="tree headings", height=8)
        self.attractions_tree.heading("#0", text="Attraction")
        self.attractions_tree.heading("Cost", text="Cost ($)")
        self.attractions_tree.heading("Time", text="Time (h)")
        self.attractions_tree.heading("Rating", text="Rating")
        self.attractions_tree.heading("Value/Cost", text="Value/Cost")
        
        self.attractions_tree.column("#0", width=150)
        self.attractions_tree.column("Cost", width=80)
        self.attractions_tree.column("Time", width=80)
        self.attractions_tree.column("Rating", width=80)
        self.attractions_tree.column("Value/Cost", width=100)
        
        self.attractions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Optimized itinerary frame
        itinerary_frame = ttk.LabelFrame(main_frame, text="Optimized Itinerary", padding="10")
        itinerary_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Itinerary treeview
        self.itinerary_tree = ttk.Treeview(itinerary_frame, columns=("Cost", "Time", "Rating"), show="tree headings", height=8)
        self.itinerary_tree.heading("#0", text="Selected Attraction")
        self.itinerary_tree.heading("Cost", text="Cost ($)")
        self.itinerary_tree.heading("Time", text="Time (h)")
        self.itinerary_tree.heading("Rating", text="Rating")
        
        self.itinerary_tree.column("#0", width=150)
        self.itinerary_tree.column("Cost", width=80)
        self.itinerary_tree.column("Time", width=80)
        self.itinerary_tree.column("Rating", width=80)
        
        self.itinerary_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Summary frame
        summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding="10")
        summary_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        self.summary_label = ttk.Label(summary_frame, text="Click 'Optimize Itinerary' to get recommendations")
        self.summary_label.grid(row=0, column=0, sticky=tk.W)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Load initial data
        self.load_attractions()
    
    def load_attractions(self):
        # Clear existing items
        for item in self.attractions_tree.get_children():
            self.attractions_tree.delete(item)
        
        # Add attractions with value/cost ratio
        for attraction in self.attractions:
            value_cost_ratio = attraction["rating"] / max(attraction["cost"], 1)  # Avoid division by zero
            self.attractions_tree.insert("", "end", text=attraction["name"],
                                       values=(f"${attraction['cost']}", 
                                             f"{attraction['time']}h",
                                             attraction["rating"],
                                             f"{value_cost_ratio:.2f}"))
    
    def fractional_knapsack(self, budget, time_limit):
        # Calculate value-to-cost ratio for each attraction
        items = []
        for i, attraction in enumerate(self.attractions):
            # Use rating as value, consider both cost and time as constraints
            weight = max(attraction["cost"], 0.1)  # Minimum weight to avoid division by zero
            value = attraction["rating"]
            ratio = value / weight
            items.append({
                'index': i,
                'name': attraction["name"],
                'cost': attraction["cost"],
                'time': attraction["time"],
                'rating': attraction["rating"],
                'ratio': ratio
            })
        
        # Sort by value-to-cost ratio in descending order
        items.sort(key=lambda x: x['ratio'], reverse=True)
        
        selected_items = []
        total_cost = 0
        total_time = 0
        total_rating = 0
        
        for item in items:
            # Check if we can add the full item
            if total_cost + item['cost'] <= budget and total_time + item['time'] <= time_limit:
                selected_items.append({
                    'name': item['name'],
                    'cost': item['cost'],
                    'time': item['time'],
                    'rating': item['rating'],
                    'fraction': 1.0
                })
                total_cost += item['cost']
                total_time += item['time']
                total_rating += item['rating']
            else:
                # Try fractional inclusion based on budget constraint
                remaining_budget = budget - total_cost
                remaining_time = time_limit - total_time
                
                if remaining_budget > 0 and remaining_time > 0 and item['cost'] > 0:
                    # Calculate fraction based on the more limiting constraint
                    budget_fraction = remaining_budget / item['cost']
                    time_fraction = remaining_time / item['time']
                    fraction = min(budget_fraction, time_fraction, 1.0)
                    
                    if fraction > 0.1:  # Only include if fraction is meaningful
                        selected_items.append({
                            'name': item['name'],
                            'cost': item['cost'] * fraction,
                            'time': item['time'] * fraction,
                            'rating': item['rating'] * fraction,
                            'fraction': fraction
                        })
                        total_cost += item['cost'] * fraction
                        total_time += item['time'] * fraction
                        total_rating += item['rating'] * fraction
                        break
        
        return selected_items, total_cost, total_time, total_rating
    
    def optimize(self):
        try:
            budget = float(self.budget_var.get())
            time_limit = float(self.time_var.get())
            
            if budget <= 0 or time_limit <= 0:
                messagebox.showerror("Error", "Budget and time must be positive values")
                return
            
            # Run fractional knapsack algorithm
            selected_items, total_cost, total_time, total_rating = self.fractional_knapsack(budget, time_limit)
            
            # Clear previous results
            for item in self.itinerary_tree.get_children():
                self.itinerary_tree.delete(item)
            
            # Display selected items
            for item in selected_items:
                name = item['name']
                if item['fraction'] < 1.0:
                    name += f" ({item['fraction']:.1%})"
                
                self.itinerary_tree.insert("", "end", text=name,
                                         values=(f"${item['cost']:.2f}",
                                               f"{item['time']:.1f}h",
                                               f"{item['rating']:.1f}"))
            
            # Update summary
            efficiency = (total_rating / max(total_cost, 1)) if total_cost > 0 else total_rating
            summary_text = (f"Total Cost: ${total_cost:.2f} | "
                          f"Total Time: {total_time:.1f}h | "
                          f"Total Rating: {total_rating:.1f} | "
                          f"Efficiency: {efficiency:.2f}")
            self.summary_label.config(text=summary_text)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for budget and time")

if __name__ == "__main__":
    root = tk.Tk()
    app = TouristOptimizer(root)
    root.mainloop()

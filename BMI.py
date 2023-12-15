import tkinter as tk
from tkinter import ttk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BMIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")

        # Connect to SQLite database
        self.conn = sqlite3.connect("bmi_data.db")
        self.create_table()

        # GUI elements
        self.label_weight = ttk.Label(root, text="Weight (kg):")
        self.label_height = ttk.Label(root, text="Height (cm):")

        self.entry_weight = ttk.Entry(root)
        self.entry_height = ttk.Entry(root)

        self.button_calculate = ttk.Button(root, text="Calculate BMI", command=self.calculate_bmi)
        self.button_view_history = ttk.Button(root, text="View History", command=self.view_history)

        # Layout
        self.label_weight.grid(row=0, column=0, padx=10, pady=10)
        self.label_height.grid(row=1, column=0, padx=10, pady=10)
        self.entry_weight.grid(row=0, column=1, padx=10, pady=10)
        self.entry_height.grid(row=1, column=1, padx=10, pady=10)
        self.button_calculate.grid(row=2, column=0, columnspan=2, pady=10)
        self.button_view_history.grid(row=3, column=0, columnspan=2, pady=10)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight REAL,
                height REAL,
                bmi REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def calculate_bmi(self):
        try:
            weight = float(self.entry_weight.get())
            height = float(self.entry_height.get())
            bmi = weight / ((height / 100) ** 2)

            # Save data to the database
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO bmi_data (weight, height, bmi) VALUES (?, ?, ?)", (weight, height, bmi))
            self.conn.commit()

            # Display BMI result
            result_text = f"Your BMI: {bmi:.2f}"
            ttk.Label(self.root, text=result_text).grid(row=4, column=0, columnspan=2, pady=10)

        except ValueError:
            ttk.Label(self.root, text="Please enter valid numeric values for weight and height.").grid(
                row=4, column=0, columnspan=2, pady=10)

    def view_history(self):
        # Retrieve data from the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT timestamp, bmi FROM bmi_data ORDER BY timestamp DESC LIMIT 10")
        data = cursor.fetchall()

        # Create a new window for historical data viewing
        history_window = tk.Toplevel(self.root)
        history_window.title("BMI History")

        # Display historical data in a table
        ttk.Label(history_window, text="Date").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(history_window, text="BMI").grid(row=0, column=1, padx=5, pady=5)

        for i, row in enumerate(data, start=1):
            ttk.Label(history_window, text=row[0]).grid(row=i, column=0, padx=5, pady=5)
            ttk.Label(history_window, text=row[1]).grid(row=i, column=1, padx=5, pady=5)

        # Create a graph for BMI trend analysis
        self.plot_bmi_trend(history_window, data)

    def plot_bmi_trend(self, history_window, data):
        timestamps = [row[0] for row in data]
        bmis = [row[1] for row in data]

        # Create a figure and axis
        fig, ax = plt.subplots()
        ax.plot(timestamps, bmis, marker='o', linestyle=':', color='green')
        ax.set_title('BMI Trend Analysis')
        ax.set_xlabel('Date')
        ax.set_ylabel('BMI')

        # Embed the matplotlib figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=history_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=len(data) + 1, column=0, columnspan=2, padx=10, pady=10)

        # Show the plot
        canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BMIApp(root)
    root.mainloop()
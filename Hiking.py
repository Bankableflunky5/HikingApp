import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import csv  
import sqlite3
import matplotlib.pyplot as plt
import os

class HikingGearManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Hiking Gear Manager")

        # Load or create the last opened database path
        self.load_or_create_database()

        self.db_conn = sqlite3.connect(self.db_location)
        self.create_table()

        self.create_widgets()
        self.create_menu()

    def load_or_create_database(self):
        config_file = "config.txt"
        if os.path.exists(config_file) and os.stat(config_file).st_size != 0:
            # Load the last opened database path
            with open(config_file, "r") as f:
                self.db_location = f.readline().strip()
        else:
            # Prompt the user to select a database file
            self.db_location = filedialog.askopenfilename(title="Select Database File", filetypes=[("SQLite databases", "*.db")])
            # Save the selected database location
            self.save_last_database()

    def save_last_database(self):
        config_file = "config.txt"
        with open(config_file, "w") as f:
            f.write(self.db_location)

    def change_database_location(self):
        new_location = filedialog.askopenfilename(title="Select Database File", filetypes=[("SQLite databases", "*.db")])
        if new_location:
            self.db_location = new_location
            self.save_last_database()  # Save the new database location
            self.db_conn = sqlite3.connect(self.db_location)
            self.load_data()
            self.calculate_total_weight()


    def create_menu(self):
        # Create a menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select database", command=self.change_database_location)
        file_menu.add_command(label="Create New Database", command=self.create_new_database)

        # Sort menu
        sort_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sort", menu=sort_menu)
        sort_menu.add_command(label="Sort by Weight", command=self.sort_by_weight)

        # Bodyweight menu
        bodyweight_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bodyweight", menu=bodyweight_menu)
        bodyweight_menu.add_command(label="Enter Bodyweight", command=self.enter_bodyweight)

        # Export menu
        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Export as CSV", command=self.export_report)

        # Visualization menu
        vis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizations", menu=vis_menu)
        vis_menu.add_command(label="Show Weight Distribution Pie Chart", command=self.show_weight_distribution_pie_chart)
        vis_menu.add_command(label="Show Gear Item Bar Chart", command=self.show_gear_item_bar_chart)
        
        # Checklist menu
        checklist_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Checklist", menu=checklist_menu)
        checklist_menu.add_command(label="Open Checklist", command=self.open_checklist)

        self.sort_count = 0

    def create_table(self):
        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS hiking_gear (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            category TEXT,
                            quantity INTEGER,
                            weight REAL,
                            checked INTEGER
                         )''')

    def show_weight_distribution_pie_chart(self):
        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("SELECT category, SUM(weight * quantity) FROM hiking_gear GROUP BY category")
            data = c.fetchall()

        categories = [row[0] for row in data]
        weights = [row[1] for row in data]

        total_weight = sum(weights)

        plt.figure(figsize=(8, 6))
        plt.pie(weights, labels=categories, autopct=lambda pct: f"{pct:.1f}% ({total_weight * pct / 100:.2f} kg)")
        plt.title("Weight Distribution by Category")
        plt.axis('equal')
        plt.show()

    def show_gear_item_bar_chart(self):
        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("SELECT name, SUM(quantity) FROM hiking_gear GROUP BY name")
            data = c.fetchall()

        if not data:
            messagebox.showinfo("No Data", "No gear items found.")
            return

        gear_items = [row[0] for row in data]
        quantities = [row[1] for row in data]

        plt.bar(gear_items, quantities)
        plt.xlabel("Gear Item")
        plt.ylabel("Quantity")
        plt.title("Gear Item Bar Chart")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def sort_by_weight(self):
        self.sort_count += 1
        
        if self.sort_count % 3 == 1:  # First click
            # Sort by weight in ascending order
            self.tree.heading("Weight", text="Weight ▲")
            self.sort_data("ASC")
        elif self.sort_count % 3 == 2:  # Second click
            # Sort by weight in descending order
            self.tree.heading("Weight", text="Weight ▼")
            self.sort_data("DESC")
        else:  # Third click
            # Reset sorting
            self.tree.heading("Weight", text="Weight")
            self.load_data()

    def sort_data(self, order):
        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("SELECT ID, Name, Category, Quantity, Weight FROM hiking_gear ORDER BY Weight " + order)
            sorted_results = c.fetchall()

        self.tree.delete(*self.tree.get_children())
        for row in sorted_results:
            self.tree.insert("", "end", values=row)

    def change_database_location(self):
        new_location = filedialog.askopenfilename(title="Select Database File", filetypes=[("SQLite databases", "*.db")])
        if new_location:
            self.db_location = new_location
            self.db_conn = sqlite3.connect(self.db_location)
            self.load_data()
            self.calculate_total_weight()

    def export_report(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                
                # Write header
                csv_writer.writerow(["ID", "Name", "Category", "Quantity", "Weight (kg)"])

                # Write item data
                with self.db_conn:
                    c = self.db_conn.cursor()
                    c.execute("SELECT ID, Name, Category, Quantity, Weight FROM hiking_gear")
                    for row in c.fetchall():
                        csv_writer.writerow(row)

                # Calculate total weight
                c.execute("SELECT SUM(Weight * Quantity) FROM hiking_gear")
                total_weight = c.fetchone()[0] or 0

                # Write total weight
                csv_writer.writerow(["Total Weight", "", "", "", f"{total_weight:.2f}"])

            messagebox.showinfo("Export Successful", "Report exported successfully.")
    
    def create_new_database(self):
        new_location = filedialog.asksaveasfilename(title="Create New Database", filetypes=[("SQLite databases", "*.db")])
        if new_location:
            # Connect to the new database
            self.db_conn = sqlite3.connect(new_location)
            self.db_location = new_location
            # Create the hiking_gear table
            self.create_table()
            # Reload data and update UI
            self.load_data()
            self.calculate_total_weight()

    def create_widgets(self):
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(padx=10, pady=10)

        btn_add_item = ttk.Button(frame_buttons, text="Add Item", command=self.add_item_window)
        btn_add_item.grid(row=0, column=0, padx=5, pady=5)

        btn_remove_item = ttk.Button(frame_buttons, text="Remove Item", command=self.remove_item)
        btn_remove_item.grid(row=0, column=1, padx=5, pady=5)

        btn_edit_item = ttk.Button(frame_buttons, text="Edit Item", command=self.edit_item_window)
        btn_edit_item.grid(row=0, column=2, padx=5, pady=5)

        lbl_search = ttk.Label(frame_buttons)
        lbl_search.grid(row=0, column=3, padx=5, pady=5, sticky=tk.E)
        self.entry_search = ttk.Entry(frame_buttons)
        self.entry_search.grid(row=0, column=4, padx=5, pady=5)
        btn_search = ttk.Button(frame_buttons, text="Search", command=self.search_item)
        btn_search.grid(row=0, column=5, padx=5, pady=5)

        frame_table = ttk.Frame(self.root)
        frame_table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame_table, columns=("ID", "Category", "Name", "Quantity", "Weight"), show="headings")
        
        # Update headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Weight", text="Weight")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.weight_info_label = ttk.Label(frame_buttons, text="")
        self.weight_info_label.grid(row=1, column=4, columnspan=2, padx=5, pady=5)

        self.load_data()
        self.calculate_total_weight()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("SELECT ID, Category, Name, Quantity, Weight FROM hiking_gear ORDER BY Category")
            for row in c.fetchall():
                self.tree.insert("", "end", values=row)
        

    def add_item_window(self):
        top = tk.Toplevel()
        top.title("Add Item")

        lbl_name = ttk.Label(top, text="Name:")
        lbl_name.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_name = ttk.Entry(top)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        lbl_category = ttk.Label(top, text="Category:")
        lbl_category.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_category = ttk.Entry(top)
        self.entry_category.grid(row=1, column=1, padx=5, pady=5)

        lbl_quantity = ttk.Label(top, text="Quantity:")
        lbl_quantity.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_quantity = ttk.Entry(top)
        self.entry_quantity.grid(row=2, column=1, padx=5, pady=5)

        lbl_weight = ttk.Label(top, text="Weight:")
        lbl_weight.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_weight = ttk.Entry(top)
        self.entry_weight.grid(row=3, column=1, padx=5, pady=5)

        btn_add = ttk.Button(top, text="Add", command=self.add_item)
        btn_add.grid(row=4, columnspan=2, padx=5, pady=5)

    def add_item(self):
        name = self.entry_name.get().strip()
        category = self.entry_category.get().strip()
        quantity_str = self.entry_quantity.get().strip()
        weight_str = self.entry_weight.get().strip()

        if not (name and category and quantity_str and weight_str):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            quantity = int(quantity_str)
            weight = float(weight_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity and weight must be numeric.")
            return

        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("INSERT INTO hiking_gear (name, category, quantity, weight, checked) VALUES (?, ?, ?, ?, ?)",
                      (name, category, quantity, weight, 0)) # Initially unchecked
        self.load_data()
        self.calculate_total_weight()

    def remove_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = self.tree.item(selected_item, "values")[0]
            if item_id:
                try:
                    with self.db_conn:
                        c = self.db_conn.cursor()
                        c.execute("DELETE FROM hiking_gear WHERE id=?", (item_id,))
                    self.load_data()
                    self.calculate_total_weight()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove item: {str(e)}")
            else:
                messagebox.showerror("Error", "Failed to retrieve selected item ID")
        else:
            messagebox.showinfo("Info", "Please select an item to remove")

    def edit_item_window(self):
        selected_item = self.tree.selection()
        if selected_item:
            top = tk.Toplevel()
            top.title("Edit Item")

            item_values = self.tree.item(selected_item, "values")

            lbl_name = ttk.Label(top, text="Name:")
            lbl_name.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            self.entry_name = ttk.Entry(top)
            self.entry_name.grid(row=0, column=1, padx=5, pady=5)
            self.entry_name.insert(tk.END, item_values[2])

            lbl_category = ttk.Label(top, text="Category:")
            lbl_category.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            self.entry_category = ttk.Entry(top)
            self.entry_category.grid(row=1, column=1, padx=5, pady=5)
            self.entry_category.insert(tk.END, item_values[1])

            lbl_quantity = ttk.Label(top, text="Quantity:")
            lbl_quantity.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            self.entry_quantity = ttk.Entry(top)
            self.entry_quantity.grid(row=2, column=1, padx=5, pady=5)
            self.entry_quantity.insert(tk.END, item_values[3])

            lbl_weight = ttk.Label(top, text="Weight:")
            lbl_weight.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            self.entry_weight = ttk.Entry(top)
            self.entry_weight.grid(row=3, column=1, padx=5, pady=5)
            self.entry_weight.insert(tk.END, item_values[4])

            btn_update = ttk.Button(top, text="Update", command=lambda: self.update_item(selected_item))
            btn_update.grid(row=4, columnspan=2, padx=5, pady=5)

    def update_item(self, selected_item):
        item_id = self.tree.item(selected_item, "values")[0]
        name = self.entry_name.get().strip()
        category = self.entry_category.get().strip()
        quantity_str = self.entry_quantity.get().strip()
        weight_str = self.entry_weight.get().strip()

        if not (name and category and quantity_str and weight_str):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            quantity = int(quantity_str)
            weight = float(weight_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity and weight must be numeric.")
            return

        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("UPDATE hiking_gear SET name=?, category=?, quantity=?, weight=? WHERE id=?",
                      (name, category, quantity, weight, item_id))
        self.load_data()
        self.calculate_total_weight()

    def calculate_total_weight(self):
        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("SELECT SUM(weight * quantity) FROM hiking_gear")
            self.total_weight = c.fetchone()[0] or 0
        self.weight_info_label.config(text=f"Total Weight: {self.total_weight:.2f} kg")


    def search_item(self):
        query = self.entry_search.get().strip()
        if query:
            with self.db_conn:
                c = self.db_conn.cursor()
                c.execute("SELECT ID, Name, Category, Quantity, Weight FROM hiking_gear WHERE name LIKE ? OR category LIKE ? OR Quantity LIKE ?", 
                        ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
                search_results = c.fetchall()
            self.tree.delete(*self.tree.get_children())
            total_weight = 0
            for row in search_results:
                self.tree.insert("", "end", values=row)
                total_weight += row[3] * row[4]
            self.weight_info_label.config(text=f"Total Weight: {total_weight:.2f} kg")
        else:
            self.load_data()
            self.calculate_total_weight()

    def enter_bodyweight(self):
        bodyweight = simpledialog.askfloat("Enter Bodyweight", "Please enter your bodyweight in kilograms:")
        if bodyweight is not None:
            self.calculate_max_weight(bodyweight)

    def calculate_max_weight(self, bodyweight):
        max_weight = bodyweight * 0.25  # maximum weight is 25% of bodyweight
        self.weight_info_label.config(text=f"Total Weight: {self.total_weight:.2f} kg\nMaximum Weight: {max_weight:.2f} kg")

    def open_checklist(self):
        checklist_window = tk.Toplevel(self.root)
        checklist_window.title("Gear Checklist")

        self.checklist_vars = {}
        with self.db_conn:
            c = self.db_conn.cursor()
            c.execute("SELECT Name, checked FROM hiking_gear")
            gear_items = c.fetchall()

        num_columns = (len(gear_items) + 14) // 15  # Calculate the number of columns needed

        for index, (name, checked) in enumerate(gear_items):
            var = tk.IntVar(value=checked)
            self.checklist_vars[name] = var
            # Calculate row and column index based on current index
            row_index = index % 15
            col_index = index // 15
            chk = ttk.Checkbutton(checklist_window, text=name, variable=var)
            chk.grid(row=row_index, column=col_index, sticky=tk.W)

        # Save button
        save_button = ttk.Button(checklist_window, text="Save", command=self.save_checklist)
        save_button.grid(row=15, column=num_columns // 2, columnspan=2, padx=5, pady=10)

        # Exit button
        exit_button = ttk.Button(checklist_window, text="Exit", command=checklist_window.destroy)
        exit_button.grid(row=16, column=num_columns // 2, columnspan=2, padx=5, pady=10)



    def save_checklist(self):
        with self.db_conn:
            c = self.db_conn.cursor()
            for name, var in self.checklist_vars.items():
                checked = var.get()
                c.execute("UPDATE hiking_gear SET checked=? WHERE name=?", (checked, name))
        messagebox.showinfo("Checklist Saved", "Checklist has been saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HikingGearManager(root)
    root.mainloop()

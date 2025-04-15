# 🥾 Hiking Gear Manager
Hiking Gear Manager is a desktop application built with Python and Tkinter to help outdoor enthusiasts organize, track, and visualize their hiking gear. It provides features like gear management, weight tracking, checklist creation, CSV export, and data visualization using SQLite and Matplotlib.

## 📦 Features
✅ Add / Edit / Remove Gear Items

🔍 Search Gear by Name, Category, or Quantity

⚖️ Real-time Total Pack Weight Calculation

📊 Weight Distribution Pie Chart & Gear Quantity Bar Chart

📁 Export Gear List as CSV

📂 Multiple Database Support

🧾 Checklist UI for Pre-hike Preparation

💪 Enter Bodyweight & Calculate Max Carry Weight (25%)

🔄 Sortable Gear Table (by weight)

## 🖥️ Interface Overview
Top Menus: File, Sort, Bodyweight, Export, Visualizations, Checklist.

Gear Table: Displays all items with columns for ID, Category, Name, Quantity, and Weight.

Action Buttons: Add, Remove, Edit, Search.

Dynamic Label: Shows total gear weight (and max allowed weight if bodyweight is entered).

## 📁 File Structure
```bash
project/
├── main.py             # Main script (contains HikingGearManager class)
├── config.txt          # Stores last-used database path
└── *.db                # Your SQLite database(s)
```
## 🔧 Installation & Setup
### 1. Clone the Repository
```bash
git clone https://github.com/Bankableflunky5/HikingApp.git
cd HikingApp
```
### 2. Install Required Packages
```bash
pip install matplotlib
```

### 3. Run the App
```bash
python Hiking.py
```
I built this to help me figure out how to lighten my hiking pack. I wanted a way to actually see where the weight was going and make smarter choices—this app is how I did that. I hope that it can help you too!

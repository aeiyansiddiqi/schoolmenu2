import re
import sqlite3

# Function to read the menu from a text file
def read_menu_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# Read the menu text from the file
menu_text = read_menu_from_file('extracted_menus.txt')

# Function to extract menu for a given day
def extract_menu(day: str):
    # Pattern for each day's menu, ending at the next day's menu or end of text
    pattern = rf"{day}'s Menu.*?(?=(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)'s Menu|$)"
    items = re.search(pattern, menu_text, re.DOTALL)

    if items:
        # Extract the menu items for the day
        menu = items.group(0).strip()
        
        # Split by line and remove leading dash for each item
        day_menu = [item[1:].strip() for item in menu.splitlines() if item.startswith("-")]
        
        return day_menu
    else:
        return None

# List of days to extract menus for
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Dictionary to hold menus for each day
week_menus = {}

# Extract menus for each day
for day in days:
    week_menus[day] = extract_menu(day)

# Connect to SQLite database (or create if it doesn't exist)
conn = sqlite3.connect('weekly_menu.db')
cursor = conn.cursor()

# Create table for menu items
cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT,
        meal_time TEXT,
        item TEXT
    )
''')

# Function to classify items by meal time
def classify_meal_time(item_text):
    if "breakfast" in item_text.lower():
        return "Breakfast"
    elif "lunch" in item_text.lower():
        return "Lunch"
    elif "dinner" in item_text.lower():
        return "Dinner"
    else:
        return "Braekfast"

# Insert menu items into the table
for day, menu_items in week_menus.items():
    if menu_items:
        meal_time = "Breakfast"  # Default meal time
        for item in menu_items:
            # Check for meal time labels
            if "Lunch" in item:
                meal_time = "Lunch"
                continue  # Skip "Lunch" label itself
            elif "Dinner" in item:
                meal_time = "Dinner"
                continue  # Skip "Dinner" label itself

            # Insert each item with the current meal time
            cursor.execute('''
                INSERT INTO menu (day, meal_time, item) 
                VALUES (?, ?, ?)
            ''', (day, meal_time, item))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Menu data has been stored in the database.")

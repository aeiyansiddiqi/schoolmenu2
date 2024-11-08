import re
import sqlite3
import requests

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
        menu = items.group(0).strip()
        day_menu = [item[1:].strip() for item in menu.splitlines() if item.startswith("-")]
        return day_menu
    else:
        return None

# List of days to extract menus for
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Dictionary to hold menus for each day
week_menus = {}
for day in days:
    week_menus[day] = extract_menu(day)

# Connect to SQLite database (or create if it doesn't exist)
conn = sqlite3.connect('weekly_menu.db')
cursor = conn.cursor()

# Create table for menu items with image_url column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT,
        meal_time TEXT,
        item TEXT,
        image_url TEXT
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
        return "Breakfast"

# Insert menu items into the table
for day, menu_items in week_menus.items():
    if menu_items:
        meal_time = "Breakfast"  # Default meal time
        for item in menu_items:
            if "Lunch" in item:
                meal_time = "Lunch"
                continue
            elif "Dinner" in item:
                meal_time = "Dinner"
                continue

            # Insert each item with the current meal time
            cursor.execute('''
                INSERT INTO menu (day, meal_time, item) 
                VALUES (?, ?, ?)
            ''', (day, meal_time, item))

# Commit changes before adding image URLs
conn.commit()

# Function to get the first image URL for a query
def get_first_image_url(query):
    api_key = "AIzaSyBW5TrzHrydzuH71BaXnVsbq4DDbOGsUso"
    search_engine_id = "92b043485a77d44ea"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "searchType": "image",
        "num": 1
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if "items" in data:
        return data["items"][0]["link"]
    else:
        return None

# Update menu items with image URLs based on item name
cursor.execute("SELECT id, item FROM menu WHERE image_url IS NULL;")
items = cursor.fetchall()
for item_id, item_name in items:
    image_url = get_first_image_url(item_name)
    if image_url:
        cursor.execute("UPDATE menu SET image_url = ? WHERE id = ?;", (image_url, item_id))
        print(f"Updated {item_name} with image URL.")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Menu data has been stored in the database with image URLs.")

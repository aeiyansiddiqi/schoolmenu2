import re

# Function to read the menu from a text file
def read_menu_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# Read the menu text from the file
menu_text = read_menu_from_file('menu_output.txt')

# Function to extract menu for a given day
def extract_menu(day: str):
    # Create regex pattern for the given day, allowing for full or abbreviated month names
    pattern = rf"{day},? (?:October|November|Oct|Nov) \d+\n(?:Mom's Kitchen & Nature's Best\n)?(.*?)(?=\n(?:Infusion|$))"
    items = re.search(pattern, menu_text, re.DOTALL)

    # Check if we found matches
    if items:
        # Extract the menu items for the day
        menu = items.group(1).strip()
        
        # Store items in a list, line by line
        day_menu = [item.strip() for item in menu.split('\n') if item.strip()]
        
        return day_menu
    else:
        return None

# List of days to extract menus for
days = [
    "Monday", "Tuesday", "Wednesday", 
    "Thursday", "Friday", "Saturday", "Sunday"
]

# Dictionary to hold menus for each day
week_menus = {}

# Extract menus for each day
for day in days:
    week_menus[day] = extract_menu(day)

# Write the items to a new file
with open('extracted_menus.txt', 'w', encoding='utf-8') as file:
    for day, menu in week_menus.items():
        if menu:
            file.write(f"{day}'s Menu (Mom's Kitchen & Nature's Best):\n")
            for item in menu:
                file.write(f"- {item}\n")
            file.write("\n")
        else:
            file.write(f"No items found for {day}'s menu.\n\n")

print("Menu data has been written to 'extracted_menus.txt'.")

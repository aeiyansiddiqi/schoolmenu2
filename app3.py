from flask import Flask, jsonify, request
import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

CORS(app)  # This allows CORS for all routes

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('weekly_menu.db')
    conn.row_factory = sqlite3.Row  # Allows us to fetch rows as dictionaries
    return conn

# Route to retrieve all menu items for the week or a specific day
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'GET':
        # Fetch menu for all days
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT day, meal_time, item FROM menu')
        items = cursor.fetchall()
        conn.close()

        # Structure menu items by day and meal time
        weekly_menu = {}
        for item in items:
            day = item['day']
            meal_time = item['meal_time']
            if day not in weekly_menu:
                weekly_menu[day] = {}
            if meal_time not in weekly_menu[day]:
                weekly_menu[day][meal_time] = []
            weekly_menu[day][meal_time].append(item['item'])

        return jsonify(weekly_menu)

    elif request.method == 'POST':
        # Add a new menu item for a specific day
        data = request.json
        day = data.get('day')
        meal_time = data.get('meal_time')
        item = data.get('item')

        if not all([day, meal_time, item]):
            return jsonify({"error": "Day, meal_time, and item are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO menu (day, meal_time, item) 
            VALUES (?, ?, ?)
        ''', (day, meal_time, item))
        conn.commit()
        conn.close()

        return jsonify({"message": "Menu item added successfully!"}), 201

# Route to retrieve the menu for a specific day
@app.route('/menu/<day>', methods=['GET'])
def get_menu_for_day(day):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT meal_time, item FROM menu WHERE day = ?
    ''', (day,))
    items = cursor.fetchall()
    conn.close()

    # Structure the items by meal time
    menu = {}
    for item in items:
        meal_time = item['meal_time']
        if meal_time not in menu:
            menu[meal_time] = []
        menu[meal_time].append(item['item'])

    if menu:
        return jsonify({day: menu})
    else:
        return jsonify({"error": f"No menu found for {day}"}), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

    

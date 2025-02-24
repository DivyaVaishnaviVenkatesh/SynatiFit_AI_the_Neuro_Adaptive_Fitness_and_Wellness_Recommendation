# setup_db.py

import sqlite3

# Function to create tables and insert data
def setup_database():
    conn = sqlite3.connect('fitness_recommend.db')
    cursor = conn.cursor()

    # Create Contact Message Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS contact_message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create Diet Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS diet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        type TEXT NOT NULL,
        calories INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create Medicine Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS medicine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        side_effects TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Create Workout Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS workout (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        level TEXT NOT NULL,
        duration INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Insert sample data
    cursor.execute("INSERT INTO contact_message (name, email, message) VALUES (?, ?, ?)", ('John Doe', 'john.doe@example.com', 'I need help with my fitness goals.'))
    cursor.execute("INSERT INTO contact_message (name, email, message) VALUES (?, ?, ?)", ('Jane Smith', 'jane.smith@example.com', 'Can you provide a workout plan for beginners?'))

    cursor.execute("INSERT INTO diet (name, description, type, calories) VALUES (?, ?, ?, ?)", ('Keto Diet', 'Low-carb, high-fat diet aimed at weight loss.', 'Keto', 1800))
    cursor.execute("INSERT INTO diet (name, description, type, calories) VALUES (?, ?, ?, ?)", ('Vegetarian Diet', 'Diet consisting mainly of plant-based foods.', 'Vegetarian', 2000))

    cursor.execute("INSERT INTO medicine (name, dosage, frequency, side_effects) VALUES (?, ?, ?, ?)", ('Ibuprofen', '200mg', 'Twice a day', 'Stomach upset'))
    cursor.execute("INSERT INTO medicine (name, dosage, frequency, side_effects) VALUES (?, ?, ?, ?)", ('Vitamin C', '500mg', 'Once a day', 'No significant side effects'))

    cursor.execute("INSERT INTO workout (name, description, level, duration) VALUES (?, ?, ?, ?)", ('Push-ups', 'A basic upper body exercise targeting chest, arms, and shoulders.', 'Beginner', 15))
    cursor.execute("INSERT INTO workout (name, description, level, duration) VALUES (?, ?, ?, ?)", ('Squats', 'A lower body exercise that targets thighs and glutes.', 'Intermediate', 20))
    cursor.execute("INSERT INTO workout (name, description, level, duration) VALUES (?, ?, ?, ?)", ('Burpees', 'A full-body exercise that combines squats, push-ups, and jumps.', 'Advanced', 25))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database setup and sample data inserted successfully!")

# Run the database setup function
if __name__ == '__main__':
    setup_database()

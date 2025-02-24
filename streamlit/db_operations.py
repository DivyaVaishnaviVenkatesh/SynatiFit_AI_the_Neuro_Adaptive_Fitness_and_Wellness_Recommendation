# db_operations.py

import sqlite3

# Function to get all contact messages
def get_all_contact_messages():
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contact_message")
    messages = cursor.fetchall()
    conn.close()
    return messages

# Function to get all diets
def get_all_diets():
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diet")
    diets = cursor.fetchall()
    conn.close()
    return diets

# Function to get all medicines
def get_all_medicines():
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicine")
    medicines = cursor.fetchall()
    conn.close()
    return medicines

# Function to get all workouts
def get_all_workouts():
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workout")
    workouts = cursor.fetchall()
    conn.close()
    return workouts

# Function to insert new contact message
def insert_contact_message(name, email, message):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contact_message (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()

# You can add other insert, update, and delete functions here as needed.

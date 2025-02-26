import streamlit as st
from streamlit_option_menu import option_menu
import json
import pandas as pd
import matplotlib
from test import *
from Custom_Diet import *
import speech_recognition as sr
import pyttsx3
import time
from PIL import Image
import sqlite3
import matplotlib.pyplot as plt
from db_operations import get_all_contact_messages, get_all_diets, get_all_medicines, get_all_workouts, \
    insert_contact_message


def read_image(file_path):
    """Reads an image file and returns its binary data as a BLOB."""
    with open(file_path, "rb") as file:
        return file.read()


# Function to initialize the database and create the required tables
def init_db():
    # Connect to SQLite database (this will create the db if it doesn't exist)
    conn = sqlite3.connect("fitness.db", timeout=10, check_same_thread=False)  # Prevent locking issues
    cursor = conn.cursor()

    # Drop old tables if needed
    cursor.execute("DROP TABLE IF EXISTS user_data")
    # Create user_data table
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            age INTEGER,
            level TEXT,
            workout_plan TEXT
        )
    ''')

    # Create contact_messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("DROP TABLE IF EXISTS diets")

    # Create diets table with the updated schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT,
            dosage TEXT,
            frequency TEXT,
            side_effects TEXT
        )
    ''')

    # Create medicines table
    cursor.execute("DROP TABLE IF EXISTS medicines")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        disease_name TEXT,
        medicine_name TEXT,
        dosage_form TEXT,
        strength TEXT,
        instructions TEXT
    )
''')

    # Create workouts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT,
            description TEXT,
            level TEXT,
            duration INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            weight REAL,
            calories_burned REAL,
            diet TEXT,
            workout TEXT,
            progress TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
     CREATE TABLE IF NOT EXISTS Gym (
	    Day TEXT NOT NULL,
        Exercise TEXT NOT NULL,
        Sets TEXT,
        Reps TEXT
        )
    ''')
    cursor.execute('''
    INSERT INTO Gym VALUES  ('lower', '01', '3', '8-10'),
						('lower', '02', '3', '15-20'),
						('lower', '03', '3', '12-15'),
						('lower', '04', '3', '15-20'),
						('lower', '05', '3', '8-10'),
						('lower', '06', '3', '15-20'),
						('upper', '07', '3', '8-10'),
						('upper', '08', '3', '10-12'),
						('upper', '09', '3', '8-10'),
						('upper', '10', '3', '10'),
						('upper', '11', '3', '10-12'),
						('upper', '12', '3', '10')
    ''')
    cursor.execute(''' 
    CREATE TABLE if not exists Exercise (
	Id TEXT PRIMARY KEY NOT NULL,
    Name TEXT,
    Link TEXT,
    Overview TEXT,
    Introductions TEXT)

    ''')
    cursor.execute('''
    INSERT OR IGNORE INTO Exercise VALUES ('01', 'Squats', 'https://www.youtube.com/embed/R2dMsNhN3DE', 'The squat is the king of all exercises, working over 256 muscles in one movement! From bodybuilders to powerlifters to competitive athletes, the squat is a staple compound exercise and should be in every workout plan.;For powerlifters, it is known as one of the “big three” lifts which includes the squat, deadlift, and bench press. For athletes, having an explosive squat is a good indicator for on field/court performance. And for bodybuilders, the squat is a compound exercise that targets nearly every muscle of your lower body and core.;The squat directly targets the muscles of the quads, but also involves the hamstrings, glutes, back, and core as well as muscles of the shoulders and arms to a lesser degree.;Not everyone is built to perform the traditional barbell back squat and it can result in some pain for certain individuals. Over the years, several squatting variations have been developed to help everyone be able to train this critical movement pattern safely.;The emphasis of the squat can be switched from the quads to the hamstrings by your foot placement. Some wear shoes with an elevated heel (or elevate their heels on plates) to focus more on the quads. Others keep a flat foot to put more pressure on the hamstrings.;At the end of the day it is important that you pick a squat variation and foot placement that works best for you and that you can perform safely.'
																						, 'Set up for the exercise by setting the barbell to just below shoulder height and loading the weight you want to use.;Stand under the bar with your feet at about shoulder width apart.;Position the bar so that it is resting on the muscles on the top of your back, not on the back of your neck. The bar should feel comfortable. If it doesn''t, try adding some padding to the bar.;Now take your hands over the back and grip the bar with a wide grip for stability.;You should now bend at the knees and straighten your back in preparation to take the weight off the rack.;Keeping your back straight and eyes up, push up through the legs and take the weight off the rack.;Take a small step back and stabilize yourself.;Keeping your eyes facing forward slowly lower your body down. Don''t lean forward as you come down. Your buttocks should come out and drop straight down.;Squat down until your thighs are parallel with the floor, and then slowly raise your body back up by pushing through your heels.;Do not lock the knees out when you stand up, and then repeat the movement.'),
							('02', 'Leg Press', 'https://www.youtube.com/embed/sEM_zo9w2ss', 'The leg press is a variation of the squat and an exercise used to target the muscles of the leg.;One can utilize the leg press to target both the quads and the hamstring muscle, depending on which portion of the foot they push through.;The leg press is commonly thought of as a machine variation of the barbell back squat. The mechanics are fairly similar, however, the leg press does not completely mimic the movement pattern of the squat. Nor does it work all of the muscle groups that the squat does.;The leg press is best used as an accessory movement to the squat, or as a primary movement in gyms which lack the necessary equipment to train the squat movement pattern.'
																						   , 'Load the machine with the desired weight and take a seat.;Sit down and position your feet on the sled with a shoulder width stance.;Take a deep breath, extend your legs, and unlock the safeties.;Lower the weight under control until the legs are roughly 45 degrees or slightly below.;Drive the weight back to the starting position by extending the knees but don’t forcefully lockout.;Repeat for the desired number of repetitions.'),
							('03', 'Leg Extension', 'https://www.youtube.com/embed/0fl1RRgJ83I', 'The seated leg extension is an isolation exercise and one used to target the muscles of the quads.;This exercise can be particularly hard on the knees. So, for those with prior knee issues, it may be beneficial to stick with other movements, preferably compound, to target your quads.;The leg extension is a great exercise for quad development and may be beneficial to include in your workout routines if your goals are more aesthetics-driven.;The leg extension can be utilized in both leg workouts and full body workouts.'
																							   , 'Select the desired resistance on the weight stack and insert the pin.;Adjust the seat so that the knees are directly in line with the axis of the machine.;Sit down and position your shins behind the pad at the base of the machine.;Take a deep breath and extend your legs as you flex your quadriceps.;As you lock out the knees, exhale to complete the repetition.;Slowly lower your feet back to the starting position and repeat for the desired number of repetitions.'),
							('04', 'Leg Press Calf Raise', 'https://www.youtube.com/embed/RcKQbiL-ZOc', 'The leg press calf raise is a variation of the machine calf raise and an exercise used to build the muscles of the calves.;The calves can be a very stubborn muscle group, so it’s important to target them with plenty of different angles and a with a high training frequency.;This exercise can be incorporated into your leg days or full body days.'
																									  , 'Load the machine with the desired weight and take a seat.;Sit down and position your feet on the sled with a shoulder width stance.;Take a deep breath, extend your legs, but keep the safeties locked (if possible).;Position your feet at the base of the platform and allow the heels to hang off.;Lower the heels by dorsiflexing the ankles until the calves are fully stretched.;Drive the weight back to the starting position by extending the ankles and flexing the calves.;Repeat for the desired number of repetitions.'),
							('05', 'Stiff Leg Deadlift', 'https://www.youtube.com/embed/CkrqLaDGvOA', 'The stiff leg deadlift is a variation of the deadlift and an exercise used primarily to target the muscles of the hamstrings.;The stiff leg deadlift has long been thought of as the “leg” deadlift variation, despite all hip hinge movements primarily targeting the hamstrings. A smart option, to increase training frequency and work on the movement pattern, would be to perform stiff legs on your leg day and another deadlift variation on your back or pull days.;The hip hinge is a crucial movement pattern, so it is important to find a variation that is comfortable for you to perform (if able), and work on it.;The stiff leg deadlift is best utilized during your leg workouts and/or full body workouts.'
																									, 'Position the bar over the top of your shoelaces and assume a hip width stance.;Push your hips back and hinge forward until your torso is nearly parallel with the floor.;Reach down and grasp the bar using a shoulder width, double overhand grip.;Ensure your spine is neutral, shin is vertical, and your hips are roughly the same height as your shoulders.;Drive through the whole foot and focus on pushing the floor away.;Ensure the bar tracks in a straight line as you extend the knees and hips.;Once you have locked out the hips, reverse the movement by pushing the hips back and hinging forward.;Return the bar to the floor, reset, and repeat for the desired number of repetitions.'),
							('06', 'Seated Calf Raise', 'https://www.youtube.com/embed/Yh5TXz99xwY', 'The seated calf raise is a variation of the machine calf raise and an exercise used to isolate the muscles of the calves.;The calves can be a stubborn muscle group for a lot of people, so it’s important to experiment with several different angles when performing calf raises. You may also want to consider training the calves with a high training frequency.;The seated calf raise can be incorporated into your leg workouts and full body workouts.'
																								   , 'Take a seat on the machine and place the balls of your feet on the platform with your toes pointed forward - your heels will naturally hang off. Position the base of quads under the knee pad and allow your hands to rest on top.;Extend your ankles and release the safety bar.;Lower the heels by dorsiflexing the ankles until the calves are fully stretched.;Extend the ankles and exhale as you flex the calves.;Repeat for the assigned number of repetitions.'),
							('07', 'Incline Bench Press', 'https://www.youtube.com/embed/uIzbJX5EVIY', 'The incline bench press is a variation of the bench press and an exercise used to build the muscles of the chest. The shoulders and triceps will be indirectly involved as well.;Utilizing an incline will allow you to better target the upper portion of the chest, a lagging part for a lot of lifters.;You can include incline bench press in your chest workouts, upper body workouts, push workouts, and full body workouts.'
																									 , 'Lie flat on an incline bench and set your hands just outside of shoulder width.;Set your shoulder blades by pinching them together and driving them into the bench.;Take a deep breath and allow your spotter to help you with the lift off in order to maintain tightness through your upper back.;Let the weight settle and ensure your upper back remains tight after lift off.;Inhale and allow the bar to descend slowly by unlocking the elbows.;Lower the bar in a straight line to the base of the sternum (breastbone) and touch the chest.;Push the bar back up in a straight line by pressing yourself into the bench, driving your feet into the floor for leg drive, and extending the elbows.;Repeat for the desired number of repetitions.'),
							('08', 'One Arm Dumbbell Row', 'https://www.youtube.com/embed/YZgVEy6cmaY', 'The one arm dumbbell row is a variation of the dumbbell row and an exercise used to build back muscle and strength.;The back is a muscle group that requires a fair amount of variation. So, experiment with several different angles and hand positions to maximize your back muscle growth.;Rows are a foundational movement pattern and are very important to train for balanced muscle growth and strength. So, experiment until you find a rowing variation that you enjoy and work on it.;The one arm dumbbell row can be performed during your back workouts, upper body workouts, pull workouts, and full body workouts.'
																									  , 'Assume a standing position while holding a dumbbell in one hand with a neutral grip.;Hinge forward until your torso is roughly parallel with the floor (or slightly above) and then begin the movement by driving the elbow behind the body while retracting the shoulder blade.;Pull the dumbbell towards your body until the elbow is at (or just past) the midline and then slowly lower the dumbbell back to the starting position under control.;Repeat for the desired number of repetitions on both sides.'),
							('09', 'Seated Barbell Press', 'https://www.youtube.com/embed/Gxhx7GpRb5g', 'The seated barbell shoulder press is a variation of the overhead press and an exercise used to build shoulder strength and muscle.;Vertical press variations, such as the seated barbell shoulder press, are crucial movement patterns to train and should be incorporated into your workout routines. So, experiment with the variations until you find one that feels comfortable for you to perform and continue to work on it.;The seated barbell shoulder press can be included in your shoulder workouts, push workouts, upper body workouts, and full body workouts.'
																									  , 'Adjust the barbell to just below shoulder height while standing then load the desired weight onto the bar.;Place an adjustable bench beneath the bar in an upright position.;Sit down on the bench and unrack the bar using a pronated grip.;Inhale, brace, tuck the chin, then lower the bar to the top of your chest.;Exhale and press the bar back to lockout.;Repeat for the desired number of repetitions.'),
							('10', 'Pull Ups', 'https://www.youtube.com/embed/5oxviYmdHCY', 'The wide grip pull up is a variation of the pull up and an exercise used to target the upper back muscles such as the latissimus dorsi.;Vertical pulling movements, such as the wide grip pull up, are foundational movements that should be included in your workout routines. So, once you’ve found a variation you like and feels comfortable to you, master it as it will benefit you from a strength and aesthetic standpoint.;The wide grip pull up can be incorporated into back workouts, pull workouts, upper body workouts, or full body workouts.'
																						  , 'Using a pronated grip, grasp the pull bar with a wider than shoulder width grip.;Take a deep breath, squeeze your glutes and brace your abs. Depress the shoulder blades and then drive the elbows straight down to the floor while activating the lats.;Pull your chin towards the bar until the lats are fully contracted, then slowly lower yourself back to the start position and repeat for the assigned number of repetitions.'),
							('11', 'Skullcrushers', 'https://www.youtube.com/embed/K6MSN4hCDM4', 'The EZ bar skullcrusher is a variation of the skullcrusher and an exercise used to strengthen the muscles of the triceps.;The triceps can be trained in many different ways to promote growth and overhead extensions, such as the EZ bar skullcrusher, are an effective way to target the long head of the tricep.;Having bigger and stronger triceps are not only important from an aesthetic standpoint but can also help contribute to better performance on pressing motions such as the bench press.'
																							   , 'Select your desired weight and sit on the edge of a flat bench.;To get into position, lay back and keep the bar close to your chest. Once you are supine, press the weight to lockout.;Lower the weights towards your head by unlocking the elbows and allowing the ez bar to drop toward your forehead or just above.;Once your forearms reach parallel or just below, reverse the movement by extending the elbows while flexing the triceps to lockout the weight.;Repeat for the desired number of repetitions.'),
							('12', 'Dumbbell Bench Press', 'https://www.youtube.com/embed/dGqI0Z5ul4k', 'The dumbbell bench press is a variation of the barbell bench press and an exercise used to build the muscles of the chest.;Often times, the dumbbell bench press is recommended after reaching a certain point of strength on the barbell bench press to avoid pec and shoulder injuries.;Additionally, the dumbbell bench press provides an ego check in the amount of weight used due to the need to maintain shoulder stability throughout the exercise.;The exercise itself can be featured as a main lift in your workouts or an accessory lift to the bench press depending on your goals.'
																									  , 'Pick up the dumbbells off the floor using a neutral grip (palms facing in). Position the ends of the dumbbells in your hip crease, and sit down on the bench.;To get into position, lay back and keep the weights close to your chest. Once you are in position, take a deep breath, and press the dumbbells to lockout at the top.;Slowly lower the dumbbells under control as far as comfortably possible (the handles should be about level with your chest).;Contract the chest and push the dumbbells back up to the starting position.;Repeat for the desired number of repetitions.')
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Dish (
    Id TEXT NOT NULL PRIMARY KEY,
    Name TEXT,
    Image BLOB,
    Nutrition TEXT,
    Recipe TEXT,
    Steps TEXT
    )
    ''')
    dish_data = [
        ('01', 'Gluten-Free Pancakes', read_image('images/dishes/01.jpg'), '176;26;6;8',
         'Cream cheese:0.5 oz;Egg:1 fruit;Honey: 1 teaspoon;Cinnamon: 1/2 teaspoon;Oatmeal: 1/2 cup',
         'Blend ingredients...'),
        
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO Dish (Id, Name, Image, Nutrition, Recipe, Steps) VALUES (?, ?, ?, ?, ?, ?)
    ''', dish_data)
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized and tables created successfully!")


# Call the init_db function to initialize the database
init_db()


# Function to insert user data into the user_data table
def insert_user_data(username, age, level, workout_plan):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_data (username, age, level, workout_plan)
            VALUES (?, ?, ?, ?)
        ''', (username, age, level, workout_plan))
        conn.commit()
        print(f"Inserted user data: Username={username}, Age={age}, Level={level}, Workout Plan={workout_plan}")
    except sqlite3.Error as e:
        print(f"Error inserting user data: {e}")
    finally:
        conn.close()


# Function to insert workout data into the workouts table
def insert_workout_data(username, name, description, level, duration):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO workouts (username, name, description, level, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, name, description, level, duration))
        conn.commit()
        print(
            f"Inserted workout data: Username={username}, Name={name}, Description={description}, Level={level}, Duration={duration}")
    except sqlite3.Error as e:
        print(f"Error inserting workout data: {e}")
    finally:
        conn.close()


# Function to insert contact message into the contact_messages table
def insert_contact_message(name, email, message):
    print(f"Debug - Inserting Contact Message: {name}, {email}, {message}")  # Debug
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO contact_messages (name, email, message)
            VALUES (?, ?, ?)
        ''', (name, email, message))
        conn.commit()
        print(f"Inserted contact message: Name={name}, Email={email}, Message={message}")
    except sqlite3.Error as e:
        print(f"Error inserting contact message: {e}")
    finally:
        conn.close()


# Function to fetch user data from the user_data table
def fetch_user_data(username):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_data WHERE username = ?', (username,))
    data = cursor.fetchall()
    conn.close()
    return data


def fetch_workouts(username):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workouts WHERE username = ?', (username,))
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_dish_data():
    """Fetch all dish data from the Dish table."""
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Dish")
    dishes = cursor.fetchall()
    conn.close()
    return dishes

# Function to display contact messages
def display_contact_messages():
    messages = get_all_contact_messages()
    for message in messages:
        st.write(f"Name: {message[1]}")
        st.write(f"Email: {message[2]}")
        st.write(f"Message: {message[3]}")
        st.write(f"Date: {message[4]}")
        st.write("---")


# Function to display diets
def display_diets():
    diets = get_all_diets()
    for diet in diets:
        st.write(f"Diet Name: {diet[1]}")
        st.write(f"Description: {diet[2]}")
        st.write(f"Type: {diet[3]}")
        st.write(f"Calories: {diet[4]}")
        st.write("---")


# Function to display medicines
def display_medicines():
    medicines = get_all_medicines()
    for medicine in medicines:
        st.write(f"Medicine Name: {medicine[1]}")
        st.write(f"Dosage: {medicine[2]}")
        st.write(f"Frequency: {medicine[3]}")
        st.write(f"Side Effects: {medicine[4]}")
        st.write("---")


# Function to display workouts
def display_workouts():
    workouts = fetch_workouts(st.session_state.username)
    for workout in workouts:
        st.write(f"Workout Name: {workout[2]}")
        st.write(f"Description: {workout[3]}")
        st.write(f"Level: {workout[4]}")
        st.write(f"Duration: {workout[5]} minutes")
        st.write("---")


# Page Basic info
st.set_page_config(
    page_title='Smart Fitness Tracker with Personalized Recommendations',
    page_icon='Fitness_bloom.png'
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "username" not in st.session_state:
    st.session_state.username = ""

import streamlit as st
import sqlite3
import speech_recognition as sr
import pyttsx3
import time

import streamlit as st
import sqlite3
import speech_recognition as sr
from gtts import gTTS
import os
import time


# Function to convert text to speech using gTTS
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("start response.mp3")  # Play the audio file

# Text-Based AI Coach
def text_ai_coach():
    st.title("📝 AI Coach (Text-Based)")
    st.write("Type your request below to get workout guidance, meal suggestions, and hydration tracking.")

    # Available commands
    st.write("**Available Commands:**")
    st.write("- 'Start workout'")
    st.write("- 'Suggest a meal'")
    st.write("- 'Track hydration'")
    st.write("- 'Stop'")

    # User Input (Text)
    user_input = st.text_input("Enter your command:", "")

    if st.button("Submit"):
        if user_input:
            command = user_input.lower()
            if "start workout" in command:
                response = "Starting your workout. Let's begin with 10 squats."
            elif "suggest a meal" in command:
                response = "I suggest a healthy salad with grilled chicken for lunch."
            elif "track hydration" in command:
                response = "How many glasses of water have you had today?"
            elif "3" in command :
                response  = "Good, Can drink more Water."
            elif "stop" in command:
                response = "Stopping the AI Coach. Have a great day!"
            else:
                response = "Sorry, I didn't understand that command. Please try again."

            st.write(f"**AI Coach:** {response}")
            speak(response)  # Convert response to speech

# Add the AI Coach to the sidebar menu
with st.sidebar:
    if st.session_state.logged_in:
        selected = option_menu(
            menu_title="SFTPR",
            options=[
                "Home", "Diet", "Workout Suggestion", "Medicine Recommender",
                "Progress Tracker", "Exercise Browser", "Recipes Browser",
                "Health Tips", "Contact", "Settings", "AI Coach"
            ],
            icons=[
                "house", "flower3", "wrench", "clipboard2-x",
                "bar-chart", "trophy", "people",
                "heart-pulse", "envelope", "gear", "robot"
            ],
            menu_icon="cast",
            default_index=0
        )
        if st.session_state.username:
            st.markdown(f"### Hello, **{st.session_state.username}** 👋")
        else:
            st.markdown("### Hello, Guest 👋 (Please login!)")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.success("Logged out successfully!")
            st.experimental_rerun()
    else:
        selected = "Login"

# Main App Logic
if selected == "AI Coach":
    text_ai_coach()




def register_user(username, password):
    """Register a new user."""
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password)
            VALUES (?, ?)
        ''', (username, password))
        conn.commit()
        st.success("Registration successful! Please log in.")
        st.session_state.show_signup = False  # Redirect to login after registration
    except sqlite3.IntegrityError:
        st.error("Username already exists. Please choose a different username.")
    except Exception as e:
        st.error(f"Error during registration: {e}")
    finally:
        conn.close()


def login_user(username, password):
    """Authenticate a user."""
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        st.session_state.user_id = user[0]
        st.session_state.username = username  # Store username in session state
        st.session_state.logged_in = True
        st.success(f"🎉 Logged in as **{username}**")
        st.experimental_rerun()
    else:
        st.error("❌ Invalid username or password.")


# Login Page
def login_page():
    # Ensure session state variables do not persist unwanted values
    if "login_username" in st.session_state:
        del st.session_state["login_username"]

    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Login</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Enter your username", key="username_input")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")

        if st.form_submit_button("Login", use_container_width=True):
            user = login_user(username, password)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.username = username
                st.session_state.logged_in = True
                st.success(f"🎉 Logged in as **{username}**")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password.")

    if st.button("Don't have an account? Sign Up"):
        st.session_state.show_signup = True
        st.experimental_rerun()


def signup_page():
    st.markdown("<h2 style='text-align: center; color: #FF5733;'>Sign Up</h2>", unsafe_allow_html=True)
    with st.form("register_form"):
        new_username = st.text_input("👤 Choose a Username", key="register_username")
        new_password = st.text_input("🔑 Password", type="password", key="register_password")
        confirm_password = st.text_input("🔄 Confirm Password", type="password", key="confirm_password")

        if st.form_submit_button("Register", use_container_width=True):
            if new_password == confirm_password:
                register_user(new_username, new_password)
            else:
                st.error("❌ Passwords do not match.")

    if st.button("Already have an account? Login"):
        st.session_state.show_signup = False
        st.experimental_rerun()


if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()


# Homepage
def homepage():
    st.title("Smart Fitness Tracker with Personalized Recommendations")

    words = '''
        <p style="font-style:italic; font-family:cursive; text-align:center; font-size:18px;">
        Smart Fitness Tracker and Personalized Recommendations is an intelligent system that provides customized suggestions  
        for diet, medicine, and workout plans based on user data.
        </p>
        <p style="font-style:italic; font-family:cursive; text-align:center; font-size:18px;">
        This machine learning-powered app uses collaborative and content-based filtering to generate personalized recommendations.
        </p>
        <p style="font-style:italic; font-family:cursive; text-align:center; font-size:18px;">
        This is a prototype of the actual system, and we plan to introduce various enhancements in the future.
        </p>
    '''

    tech_stack = '''
        <ul style="font-size:16px;">
            <li style="font-style:italic; font-family:cursive;">Dataset: CSV, JSON Files</li>
            <li style="font-style:italic; font-family:cursive;">Libraries: Pandas, Numpy, Sklearn, Streamlit, Json</li>
            <li style="font-style:italic; font-family:cursive;">Programming: Python, Jupyter Notebook</li>
            <li style="font-style:italic; font-family:cursive;">Visualization: Matplotlib, Plotly</li>
        </ul>
    '''

    # Load static images
    image = Image.open('first.jpg')  # Static Image
    gif_path = "motive.gif"  # Add the path to your GIF

    # Layout with two columns
    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown(words, unsafe_allow_html=True)
    with right_column:
        st.image(image, use_column_width=True)  # Show static image

    # Display the GIF with proper alignment
    st.markdown("<h2 style='text-align:center;'>Stay Motivated 💪</h2>", unsafe_allow_html=True)
    st.image(gif_path, use_column_width=True, width = 400)  # Display the GIF

    st.title('Dataset')
    st.subheader("User Data from Database:")

    # Fetch user data using session state
    if st.session_state.username:
        user_data = fetch_user_data(st.session_state.username)
        if user_data:
            st.dataframe(pd.DataFrame(user_data, columns=["ID", "Username", "Age", "Level", "Workout Plan"]))
        else:
            st.write("No user data found.")
    else:
        st.write("Please log in to view user data.")

    # Hardcoded dataset path
    dataset_path = "dish_data.csv"  # Change this to your dataset path

    # Load dataset
    st.subheader("Loaded Dataset:")
    try:
        if dataset_path.endswith('.csv'):
            data = pd.read_csv(dataset_path)
            st.success("CSV file loaded successfully!")
        elif dataset_path.endswith('.json'):
            data = pd.read_json(dataset_path)
            st.success("JSON file loaded successfully!")
        else:
            st.error("Unsupported file format. Please provide a CSV or JSON file.")
            return

        # Display the loaded dataset
        st.dataframe(data)

        # Display basic statistics
        

    except FileNotFoundError:
        st.error(f"File not found at path: {dataset_path}. Please check the path and try again.")
    except Exception as e:
        st.error(f"Error loading dataset: {e}")

    st.title('Tech Stack')
    st.markdown(tech_stack, unsafe_allow_html=True)

if selected == 'Home':
    homepage()


# Defining CSS file
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Loading CSS
local_css('style.css')


def progress_tracker():
    st.title("🏋️ Track Your Progress")
    st.write("Log your workouts and health journey.")

    # User input fields
    username = st.text_input("Enter Your Username")
    weight = st.number_input("Enter Your Current Weight (kg)", min_value=30.0, max_value=200.0)
    calories = st.number_input("Calories Burned Today", min_value=0)
    diet = st.text_area("Describe Your Diet")
    workout = st.text_area("Describe Your Workout")
    progress = st.text_area("Your Overall Progress Notes")

    if st.button("Save Progress"):
        if username:
            conn = sqlite3.connect('fitness.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO progress_tracker (username, weight, calories_burned, diet, workout, progress)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, weight, calories, diet, workout, progress))
            conn.commit()
            conn.close()
            st.success("✅ Progress saved successfully!")
        else:
            st.warning("⚠️ Please enter a username.")

    # Fetch and visualize data
    st.subheader("📊 Your Progress Overview")
    conn = sqlite3.connect('fitness.db')
    df = pd.read_sql("SELECT * FROM progress_tracker WHERE username = ?", conn, params=(username,))
    conn.close()

    if not df.empty:
        st.write("### Recent Entries")
        st.dataframe(df)

        # Weight Progress Chart
        st.write("### 📉 Weight Progress Over Time")
        fig, ax = plt.subplots()
        ax.plot(df['timestamp'], df['weight'], marker='o', linestyle='-')
        ax.set_xlabel("Date")
        ax.set_ylabel("Weight (kg)")
        ax.set_title("Weight Progress")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Calories Burned Chart
        st.write("### 🔥 Calories Burned Over Time")
        fig, ax = plt.subplots()
        ax.bar(df['timestamp'], df['calories_burned'], color='orange')
        ax.set_xlabel("Date")
        ax.set_ylabel("Calories Burned")
        ax.set_title("Calories Burned Progress")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("ℹ️ No progress data found. Start logging your progress!")


if selected == "Progress Tracker":
    progress_tracker()

# Set initial theme to Dark
if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # Default to dark mode


def apply_theme():
    """Applies the selected theme using CSS injection."""
    if st.session_state.theme == "dark":
        dark_theme = """
        <style>
            body, .stApp { background-color: #0E1117; color: #FFFFFF; }

            /* Text and headings */
            h1, h2, h3, h4, h5, h6, p, div, span, label { color: #FFFFFF; }


            /* Input fields */
            .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
                color: #FFFFFF; 
                background-color: #1E1E1E; 
                border: 1px solid #333333;
            }

            /* Select boxes */
            .stSelectbox>div>div>select, .stRadio>div>div>label { 
                color: #FFFFFF; 
                background-color: #1E1E1E; 
            }

            /* Buttons */
            .stButton>button { 
                color: #FFFFFF; 
                background-color: #4CAF50; 
                border: 1px solid #4CAF50; 
            }

            /* Dataframes */
            .stDataFrame { color: #FFFFFF; background-color: #1E1E1E; }
        </style>
        """
        st.markdown(dark_theme, unsafe_allow_html=True)

    else:
        light_theme = """
    <style>
    body, .stApp { background-color: #FFFFFF; color: #000000; }

    /* Text and headings */
    h1, h2, h3, h4, h5, h6, p, div, span, label { color: #000000 !important; }

    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        color: #000000 !important; 
        background-color: #F0F2F6 !important; 
        border: 1px solid #CCCCCC !important;
    }

    /* Select boxes & Radio buttons */
    .stSelectbox>div>div>select, .stRadio>div>div>label { 
        color: #FFFFFF !important; 
        background-color: #F0F2F6 !important; 
    }

    /* Fix for dropdown options */
    .stSelectbox>div>div>select option {
        color: #FFFFFF !important;
        background-color: #FFFFFF !important;
    }

    /* Buttons */
    .stButton>button { 
        color: #FFFFFF !important; 
        background-color: #4CAF50 !important; 
        border: 1px solid #4CAF50 !important; 
    }

    /* Dataframes */
    .stDataFrame { color: #000000 !important; background-color: #F0F2F6 !important; }
   </style>

        """
        st.markdown(light_theme, unsafe_allow_html=True)


def settings():
    st.title("Settings")

    # Theme Selection Dropdown
    theme = st.selectbox("Choose Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "dark" else 1)

    # Update theme state
    st.session_state.theme = "light" if theme == "Light" else "dark"

    # Apply selected theme
    apply_theme()
    st.success(f"Theme set to {theme} mode!")


# Apply theme at startup
apply_theme()

if selected == "Settings":
    settings()

# Custom CSS for Improved Styling
st.markdown("""
    <style>
        .tip-box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.1);
            font-size: 20px;
            text-align: center;
            color: #333;
            font-weight: bold;
            margin: 20px auto;
            width: 80%;
        }

        .btn-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
        }

        .btn {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.3s ease;
        }

        .btn:hover {
            transform: scale(1.05);
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
        }

        .btn-wrapper {
            display: flex;
            justify-content: center;
            margin-top: 15px;
        }
    </style>
""", unsafe_allow_html=True)


def health_tips():
    st.title("💡 Daily Health Tips")

    tips = [
        "💧 **Stay Hydrated:** Drink at least 2 liters of water daily.",
        "🏋️ **Stay Active:** Exercise at least 30 minutes every day.",
        "🥦 **Eat Right:** Include fiber, protein, and healthy fats in your diet.",
        "😴 **Get Enough Sleep:** Aim for 7-9 hours of sleep for better health.",
        "👀 **Reduce Screen Time:** Take short breaks to rest your eyes.",
        "🧘 **Practice Mindfulness:** Deep breathing helps reduce stress.",
        "🪑 **Improve Posture:** Sit upright to avoid back pain.",
        "🚫🍭 **Limit Sugar Intake:** Too much sugar can lead to health issues."
    ]

    if "tip_index" not in st.session_state:
        st.session_state.tip_index = 0

    # Display current tip inside a styled box
    st.markdown(
        f'<div style="background-color: {"#1E1E1E" if st.session_state.theme == "dark" else "#F0F2F6"}; '
        f'padding: 20px; border-radius: 10px; color: {"#FFFFFF" if st.session_state.theme == "dark" else "#000000"};'
        f'">{tips[st.session_state.tip_index]}</div>',
        unsafe_allow_html=True
    )

    # Centered navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        btn_prev, btn_next = st.columns([1, 1])

        with btn_prev:
            if st.button("⬅ Previous", key="prev_btn"):
                st.session_state.tip_index = (st.session_state.tip_index - 1) % len(tips)

        with btn_next:
            if st.button("Next ➡", key="next_btn"):
                st.session_state.tip_index = (st.session_state.tip_index + 1) % len(tips)


if selected == "Health Tips":
    health_tips()


# Contact Form Frontend
def form():
    with st.container():
        st.write("---")
        st.header('Get In Touch With Me!')
        st.write('##')

        # Input fields for the contact form
        name = st.text_input('Your Full Name', key='name')
        email = st.text_input('Your Email ID', key='email')
        message = st.text_area('Your Message', key='message')

        # Submit button
        if st.button('Send'):
            # Check if all fields are filled
            if name and email and message:
                # Insert the contact message into the database
                insert_contact_message(name, email, message)
                st.success("Message sent successfully!")
            else:
                st.warning("Please fill in all fields before submitting.")


if selected == 'Contact':
    form()

# Exercise JSON Dataset
exercise_by_level = {
    'beginner': {
        'Monday': ['20 Squats', '10 Push-ups', '10 Lunges Each leg', '15 seconds Plank', '30 Jumping Jacks'],
        'Tuesday': ['20 Squats', '10 Push-ups', '10 Lunges Each leg', '15 seconds Plank', '30 Jumping Jacks'],
        'Wednesday': ['15 minutes Walk', '30 seconds Jump rope(2 reps)', '20 seconds Cobra Stretch'],
        'Thursday': ['25 Squats', '12 Push-ups', '12 Lunges Each leg', '15 seconds Plank', '30 Jumping Jacks'],
        'Friday': ['25 Squats', '12 Push-ups', '12 Lunges Each leg', '15 seconds Plank', '30 Jumping Jacks'],
        'Saturday': ['15 minutes Walk', '30 seconds Jump rope(2 reps)', '20 seconds Cobra Stretch']
    },
    'intermediate': {
        'Monday': ['3 Set Squats(8-12 reps)', '3 Set Leg Extension(8-12 reps)', '3 Set Lunges(10 reps Each)',
                   '30 Seconds Skipping(2 reps)'],
        'Tuesday': ['3 Set Bench Press(12 reps)', '3 Set Dumb-bell incline press(8-12 reps)',
                    '3 Set Cable Crossovers(10-12 reps)', '30 Seconds Boxing Skip(2 reps)'],
        'Wednesday': ['3 Set Deadlifts(6-12 reps)', '3 Set Barbell Curls(8-12 reps)', '3 Set Incline Curls(8-12 reps)'],
        'Thursday': ['3 Set Shoulder Press(8-10 reps)', '3 Set Incline Lateral Raises(8-10 reps)',
                     '3 Set Sit-ups(10-12 reps)', '2 Set Leg Raises(8-12 reps)'],
        'Friday': ['10 minutes Brisk Walk', '1 minute Skipping', 'Breathing Exercises'],
        'Saturday': ['10 minutes Brisk Walk', '1 minute Skipping', 'Breathing Exercises']
    },
    'advanced': {
        'Monday': ['5 Set Squats(8-12 reps)', '5 Set Leg Extension(8-12 reps)', '5 Set Lunges(10 reps Each)',
                   '60 Seconds Skipping(2 reps)'],
        'Tuesday': ['5 Set Bench Press(12 reps)', '5 Set Dumb-bell incline press(8-12 reps)',
                    '5 Set Cable Crossovers(10-12 reps)', '60 Seconds Boxing Skip(2 reps)'],
        'Wednesday': ['5 Set Deadlifts(6-12 reps)', '5 Set Barbell Curls(8-12 reps)', '5 Set Incline Curls(8-12 reps)'],
        'Thursday': ['5 Set Shoulder Press(8-10 reps)', '5 Set Incline Lateral Raises(8-10 reps)',
                     '5 Set Sit-ups(10-12 reps)', '4 Set Leg Raises(8-12 reps)'],
        'Friday': ['20 minutes Brisk Walk', '2 minute Boxing Skip', 'Breathing Exercises'],
        'Saturday': ['25 minutes Brisk Walk', '1 minute Skipping', 'Breathing Exercises']
    }
}


def generate_workout(level):
    # Return the workout plan for the selected level
    return exercise_by_level[level]


# For Workout Suggestion
if selected == 'Workout Suggestion':
    st.title('Personalized Workout Recommender')

    age = st.selectbox('Age', ['Select', 'Less than 18', '18 to 49', '49 to 60', 'Above 60'])
    duration = st.radio('Workout Duration:', ['Less frequently', 'Moderate', 'More Frequently'])
    level = st.selectbox('Select your level:', ['Select', 'beginner', 'intermediate', 'advanced'])
    button = st.button('Recommend Workout')

    if button:
        if level == 'Select':
            st.warning('Insertion error!! Re-check the input fields')
        else:
            nums = 1  # Initialize counter for days
            workout_plan = generate_workout(level)

            # Define days of the week explicitly
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            workout_data = []  # List to store workout details for visualization

            for day in days_of_week:
                if day == "Sunday":
                    st.markdown(
                        f"""
                        <h4>Your Workout Plan for Day {nums}: {day}</h4>
                        <div class="sundays">
                            <p style="color:#7FFF00; font-style:italic; font-family:cursive;">Take rest and go for a light walk in the park.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    workout_data.append({"Day": day, "Workout Count": 0})  # No workouts on Sunday
                else:
                    exercises = exercise_by_level[level].get(day, ["No workout assigned"])
                    exercise_str = ", ".join(exercises)
                    insert_workout_data(st.session_state.username, f"Day {nums} Workout ({day})", exercise_str, level,
                                        30)

                    st.markdown(
                        f"""
                        <h4>Your Workout Plan for Day {nums}: {day}</h4>
                        <div class="workout">
                            <div class="workout-info">
                                <p style="color:#7FFF00; font-style:italic; font-family:cursive;">Workout: {exercise_str}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    workout_data.append({"Day": day, "Workout Count": len(exercises)})

                nums += 1  # Increment day counter

            # Insert user workout details into the user_data table
            insert_user_data(st.session_state.username, age, level, str(workout_plan))

            # Convert data to Pandas DataFrame
            df = pd.DataFrame(workout_data)

            # Create a bar chart for workout distribution
            st.subheader("📊 Workout Distribution Over the Week")
            fig = px.bar(df, x="Day", y="Workout Count", title="Number of Workouts per Day",
                         labels={"Workout Count": "Number of Exercises"},
                         color="Workout Count", height=400)
            st.plotly_chart(fig)

# For Medicine Recommender
if selected == 'Medicine Recommender':
    main_1()

# For custom food recommendations
if selected == 'Diet':
    diet()


# Function to load exercises from SQLite
def load_exercises():
    conn = sqlite3.connect("fitness.db")  # Ensure correct database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Exercise")
    exercises = cursor.fetchall()
    conn.close()
    return exercises


# Function to display the Exercise Browser
def exercise_browser():
    st.markdown("<h1 style='text-align: center'>Exercise Browser</h1>", unsafe_allow_html=True)

    exercises = load_exercises()
    exercise_keywords = [""] + [e[1] for e in exercises]  # e[1] is Exercise Name

    exercise_keyword = st.selectbox("**Search Exercise**", tuple(exercise_keywords))

    if exercise_keyword:
        conn = sqlite3.connect("fitness.db")  # Ensure correct database
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Exercise WHERE Name = ?", (exercise_keyword,))
        exercise_result = cursor.fetchone()
        conn.close()

        if exercise_result:
            st.markdown(f"<h2 style='text-align: center'>{exercise_result[1]}</h2>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([0.15, 1.7, 0.15])
            with col2:
                st.markdown(f"""
                    <iframe width="100%" height="500px" allow="fullscreen;" src="{exercise_result[2]}"></iframe>
                """, unsafe_allow_html=True)

                st.subheader("I. Overview")
                st.write(exercise_result[3].replace(';', '\n'))

                st.subheader("II. Instructions")
                instructions_list = exercise_result[4].split(';')
                instructions_html = "<ul style='list-style-type: decimal; padding-left: 22px'>"
                for instruction in instructions_list:
                    instructions_html += f"<li>{instruction}</li>"
                instructions_html += "</ul>"

                st.markdown(instructions_html, unsafe_allow_html=True)


if selected == "Exercise Browser":
    exercise_browser()


class Diet():
    def __init__(self, calories, nutrition, breakfast, lunch, dinner):
        self.calories = calories
        self.nutrition = nutrition
        self.breakfast = breakfast
        self.lunch = lunch
        self.dinner = dinner

    def get_nutrition_detail(self):
        tmp = self.nutrition.split(';')
        return NutritionDetail(float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3]))

    def get_breakfast_detail(self):
        tmp = self.breakfast.split(':')
        calories = tmp[0]
        temp = tmp[1].split(';')
        id1, amount1 = temp[0].split('x')
        id2, amount2 = temp[1].split('x')
        return DietDetail(calories, id1, amount1, id2, amount2)

    def get_lunch_detail(self):
        tmp = self.lunch.split(':')
        calories = tmp[0]
        temp = tmp[1].split(';')
        id1, amount1 = temp[0].split('x')
        id2, amount2 = temp[1].split('x')
        return DietDetail(calories, id1, amount1, id2, amount2)

    def get_dinner_detail(self):
        tmp = self.dinner.split(':')
        calories = tmp[0]
        temp = tmp[1].split(';')
        id1, amount1 = temp[0].split('x')
        id2, amount2 = temp[1].split('x')
        return DietDetail(calories, id1, amount1, id2, amount2)


class NutritionDetail():
    def __init__(self, calories, carbs, fat, protein):
        self.calories = calories
        self.carbs = carbs
        self.fat = fat
        self.protein = protein

    def get_carbs_percentage(self):
        c = self.carbs * 4 / (self.carbs * 4 + self.fat * 9 + self.protein * 4)
        return c

    def get_fat_percentage(self):
        f = self.fat * 9 / (self.carbs * 4 + self.fat * 9 + self.protein * 4)
        return f

    def get_protein_percentage(self):
        p = self.protein * 4 / (self.carbs * 4 + self.fat * 9 + self.protein * 4)
        return p


class DietDetail():
    def __init__(self, calories, id1, amount1, id2, amount2):
        self.calories = calories
        self.id1 = id1
        self.amount1 = amount1
        self.id2 = id2
        self.amount2 = amount2


class Dish():
    def __init__(self, id, name, image, nutrition, recipe, steps):
        self.id = id
        self.name = name
        self.image = image
        self.nutrition = nutrition
        self.recipe = recipe
        self.steps = steps

    def get_nutrition_detail(self):
        tmp = self.nutrition.split(';')
        return NutritionDetail(float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3]))

    def get_recipe_detail(self):
        tmp = self.recipe.split(';')
        ingredients = {}
        for s in tmp:
            temp = s.split(':')
            ingredients[temp[0]] = temp[1].strip()
        return RecipeDetail(ingredients)

    def get_steps_detail(self):
        tmp = self.steps.split(';')
        steps = {}
        for i in range(0, len(tmp)):
            key = 'Step ' + str(i + 1) + ':'
            value = tmp[i]
            steps[key] = value
        return StepsDetail(steps)


class RecipeDetail():
    def __init__(self, ingredients):
        self.ingredients = ingredients


class StepsDetail():
    def __init__(self, steps):
        self.steps = steps


# Function to load dishes from SQLite
def load_dishes():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Dish")
    dishes = cursor.fetchall()
    conn.close()
    return dishes


# Function to get dish details
def get_dish_by_name(name):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Dish WHERE Name = ?", (name,))
    dish = cursor.fetchone()
    conn.close()
    return dish


# Function to Display the Food & Recipe Browser
def food_browser():
    # Apply custom CSS styles inside the function
    st.markdown(
        f"""
            <style>
                .css-18ni7ap.e8zbici2 {{
                    opacity: 0;
                }}
                .css-h5rgaw.egzxvld1 {{
                    opacity: 0;
                }}
                .block-container.css-91z34k.egzxvld4 {{
                    width: 100%;
                    padding: 0.5rem 1rem 10rem;
                    max-width: none;
                }}
                .css-uc76bn.e1fqkh3o9 {{
                    padding-top: 2rem;
                    padding-bottom: 0.25rem;
                }}
            </style>
        """, unsafe_allow_html=True
    )

    # Center Logo and Title inside food_browser
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 0.5, 1, 0.75, 1, 0.75, 0.5, 0.5])
    with col4:
        st.image(image='images/logo.png', width=140)

    # Main content of Food Browser starts here
    st.markdown("<h1 style='text-align: center'> Recipe Browser </h1>", unsafe_allow_html=True)

    # Fetch dish data from the database
    dishes = fetch_dish_data()
    dish_keywords = [""] + sorted([d[1] for d in dishes])  # d[1] is Dish Name

    dish_keyword = st.selectbox("**Search Dish**", tuple(dish_keywords))

    if dish_keyword:
        dish_result = get_dish_by_name(dish_keyword)

        if dish_result:
            dish_id, dish_name, dish_image, nutrition, recipe, steps = dish_result

            st.markdown(f"<h2 style='text-align: center'>{dish_name}</h2>", unsafe_allow_html=True)

            # Display Image (Handle NULL Values)
            col1, col2, col3 = st.columns([1.3, 0.55, 0.15])
            with col1:
                if dish_image:
                    encoded_image = base64.b64encode(dish_image).decode("utf-8")
                    st.markdown(
                        f"""
                            <p style="text-align: right">
                                <img src="data:image/jpeg;base64,{encoded_image}" width="90%">
                            </p>
                            """, unsafe_allow_html=True
                    )
                else:
                    st.warning("⚠ No image available for this dish.")

            # Display Nutrition Info
            with col2:
                nutrition_values = nutrition.split(";") if nutrition else ["0", "0", "0", "0"]
                cal, carbs, fat, protein = map(float, nutrition_values)  # Convert to float

                st.markdown(f"""
                        <table style="width:100%">
                            <tr><th style="font-size: 22px;">Nutrition</th></tr>
                            <tr>
                                <td>
                                    <b>Calories:</b> <text style="float:right">{round(cal)} cal</text><br/>
                                    <b>Carbs:</b> <text style="float:right">{carbs} g</text><br/>
                                    <b>Fat:</b> <text style="float:right">{fat} g</text><br/>
                                    <b>Protein:</b> <text style="float:right">{protein} g</text><br/>
                                </td>
                            </tr>
                        </table>
                        <br/>
                        <div class="figure_title" style="text-align:center; font-size:20px"><b>Percent Calories From:</b></div>
                    """, unsafe_allow_html=True)

                # Pie Chart for Nutrition Distribution
                matplotlib.rcParams.update({'font.size': 5})
                labels = ['Carbs', 'Fat', 'Protein']
                colors = ['#F7D300', '#38BC56', '#D35454']
                data = [carbs, fat, protein]
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.pie(data, labels=labels, colors=colors, explode=(0.15, 0.075, 0.075), autopct='%1.1f%%',
                       startangle=90,
                       wedgeprops={"edgecolor": "black", 'linewidth': 1, 'antialiased': True})
                ax.axis('equal')
                st.pyplot(fig)

            # Display Recipe & Steps
            col1, col2, col3, col4 = st.columns([0.122, 0.45, 1.278, 0.15])

            # Recipe Section
            with col2:
                recipe_table = "<table style='width: 100%;'><tr><th style='font-size: 22px;'>Recipe</th></tr><tr><td>"
                if recipe:
                    for item in recipe.split(";"):
                        ingredient, amount = item.split(":")
                        recipe_table += f"<b>{ingredient}:</b> <text style='float:right'>{amount}</text><br/>"
                else:
                    recipe_table += "No recipe available."
                recipe_table += "</td></tr></table>"
                st.markdown(recipe_table, unsafe_allow_html=True)

            # Steps Section
            with col3:
                steps_table = "<table style='width: 100%;'><tr><th colspan='2' style='font-size: 22px;'>Steps to Cook</th></tr>"
                if steps:
                    for i, step in enumerate(steps.split(";"), 1):
                        steps_table += f"<tr><td style='width: 80px; vertical-align: top'><b>Step {i}</b></td><td>{step}</td></tr>"
                else:
                    steps_table += "<tr><td>No steps available.</td></tr>"
                steps_table += "</table>"
                st.markdown(steps_table, unsafe_allow_html=True)

if selected == "Rescipes Browser":
    food_browser()


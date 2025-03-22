import json
import streamlit as st
import pandas as pd
import ydata_profiling as pp  # Ensure this is version 3.1.0
import altair as alt
import random
import base64
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import tensorflow as tf
import pickle


def insert_diet_data(username, name, dosage, frequency, side_effects):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO diets (username, name, dosage, frequency, side_effects)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, name, dosage, frequency, side_effects))
        conn.commit()
        print(f"Inserted diet data: Username={username}, Name={name}, Dosage={dosage}, Frequency={frequency}, Side Effects={side_effects}")
    except sqlite3.Error as e:
        print(f"Error inserting diet data: {e}")
    finally:
        conn.close()

def fetch_diets(username):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM diets WHERE username = ?', (username,))
    data = cursor.fetchall()
    conn.close()
    return data

class Person:
    def __init__(self, age, height, weight, gender, activity, weight_loss):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.weight_loss = weight_loss

    def calculate_bmi(self):
        bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        return bmi

    def display_result(self):
        bmi = self.calculate_bmi()
        bmi_string = f'{bmi} kg/m²'
        if bmi < 18.5:
            category = 'Underweight'
            color = 'Red'
        elif 18.5 <= bmi < 25:
            category = 'Normal'
            color = 'Green'
        elif 25 <= bmi < 30:
            category = 'Overweight'
            color = 'Yellow'
        else:
            category = 'Obesity'
            color = 'Red'
        return bmi_string, category, color

    def calculate_bmr(self):
        if self.gender == 'Male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return bmr

    def calories_calculator(self):
        activites = ['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights = [1.2, 1.375, 1.55, 1.725, 1.9]
        weight = weights[activites.index(self.activity)]
        maintain_calories = self.calculate_bmr() * weight
        return maintain_calories


class Display:
    def __init__(self):
        self.plans = ["Maintain weight", "Mild weight loss", "Weight loss", "Extreme weight loss"]
        self.weights = [1, 0.9, 0.8, 0.6]
        self.losses = ['-0 kg/week', '-0.25 kg/week', '-0.5 kg/week', '-1 kg/week']

    def display_bmi(self, person):
        st.header('BMI CALCULATOR')
        bmi_string, category, color = person.display_result()
        st.metric(label="Body Mass Index (BMI)", value=bmi_string)
        new_title = f'<p style="font-family:sans-serif; color:{color}; font-size: 25px;">{category}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.markdown(
            """
            Healthy BMI range: 18.5 kg/m² - 25 kg/m².
            """)

    def display_calories(self, person):
        st.header('CALORIES CALCULATOR')
        maintain_calories = person.calories_calculator()
        st.write('The results show a number of daily calorie estimates that can be used as a guideline for how many calories to consume each day to maintain, lose, or gain weight at a chosen rate.')
        for plan, weight, loss, col in zip(self.plans, self.weights, self.losses, st.columns(4)):
            with col:
                st.metric(label=plan, value=f'{round(maintain_calories * weight)} Calories/day', delta=loss, delta_color="inverse")


# Load the pandas dataframe and perform automated Exploratory Data Analysis
def profiling():
    data = pd.read_csv('diet_data_csv.csv', compression='gzip')
    profiles = data.iloc[:, :].head(150)
    profile = pp.ProfileReport(profiles, minimal=True)
    profile.to_html("output.html")


# Load the Output dataset
def load_data(file_name):
    data = pd.read_csv(file_name)
    return data
# Load diet dataset
df = load_data("dish_data.csv")

# ✅ Ensure the 'Nutrition' column is correctly split
if "Nutrition (Calories;Carbs;Fat;Protein)" in df.columns:
    df[['Calories', 'Carbs', 'Fat', 'Protein']] = df['Nutrition (Calories;Carbs;Fat;Protein)'].str.split(';',
                                                                                                         expand=True)

    # Convert extracted columns to numeric
    df['Calories'] = pd.to_numeric(df['Calories'], errors='coerce')
    df['Carbs'] = pd.to_numeric(df['Carbs'], errors='coerce')
    df['Fat'] = pd.to_numeric(df['Fat'], errors='coerce')
    df['Protein'] = pd.to_numeric(df['Protein'], errors='coerce')

    # Drop the original Nutrition column (optional, if no longer needed)
    df.drop(columns=['Nutrition (Calories;Carbs;Fat;Protein)'], inplace=True)
else:
    raise KeyError("❌ 'Calories' column is missing in the dataset! Check column names.")


# Generate random suggestions
def get_suggestion(data, n):
    if data is not None and isinstance(data, pd.DataFrame):
        # Sample n random rows from the DataFrame
        return data.sample(n=n)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if data is invalid


# Convert JSON to Dataframe
def get_data(data):
    # Ensure the DataFrame has the required columns
    required_columns = ['Dish Name', 'Ingredients', 'Calories', 'Instructions']
    if all(col in data.columns for col in required_columns):
        return data[required_columns]
    else:
        st.error("CSV file is missing required columns.")
        return pd.DataFrame()

import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import tensorflow as tf
import pickle
import numpy as np
import pandas as pd
import streamlit as st

# Load ANN Model & Scaler
model = tf.keras.models.load_model("diet_ann_model.h5")
#scaler = pickle.load(open("scaler.pkl", "rb"))


# Diet Recommendation
def display_recommendation(dataset):
    st.header('DIET RECOMMENDER')

    if "Dish Name" not in dataset.columns or "Calories" not in dataset.columns:
        st.error("⚠️ Missing required columns in dataset!")
        return

    with st.spinner('Generating recommendations...'):
        st.subheader('Recommended recipes:')
        recipes = dataset

        for index, row in recipes.iterrows():
            recipe_name = row.get("Dish Name", "Unknown Dish")  # Use .get() to prevent KeyError
            ingredients = row.get("Ingredients", "Ingredients not available")  # Handle missing column
            calories = row.get("Calories", "N/A")
            instructions = row.get("Instructions", "Instructions not available")

            dosage = "Not available"
            frequency = "Not available"
            side_effects = "Not available"

            if "username" in st.session_state:
                insert_diet_data(st.session_state.username, recipe_name, dosage, frequency, side_effects)

            expander = st.expander(recipe_name)
            expander.markdown(f"### 🍽️ Ingredients: \n- {ingredients}")
            expander.markdown(f"### 🍳 Recipe Instructions: \n- {instructions}")
            expander.markdown(f"### 🔥 Calories: {calories}")


# Load PDF File
def displayPDF(file):
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# Visualize Scatter Plot 'Calories Per Recipe'
def display_charts(dataset):
    # Ensure 'Nutrition (Calories;Carbs;Fat;Protein)' exists
    if 'Nutrition (Calories;Carbs;Fat;Protein)' in dataset.columns:
        # Split the column into separate nutrition values
        nutrition_split = dataset['Nutrition (Calories;Carbs;Fat;Protein)'].str.split(';', expand=True)
        #Rename the new columns
        dataset[['Calories', 'Carbs', 'Fat', 'Protein']] = nutrition_split
        #Convert 'Calories' to numeric
        dataset['Calories'] = pd.to_numeric(dataset['Calories'], errors='coerce')
  # Now use the corrected dataset in the scatter plot
    fig = px.scatter(dataset, x='Dish Name', y='Calories', size='Calories',
                 hover_data=['Ingredients', 'Instructions'])

    st.markdown(f"""<h3 style="color:#7FFF00;">Calories per Recipe</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig)


# Heatmap of the dataset
def display_heatmap(dataset):
    fig = go.Figure(data=go.Heatmap(
        z=dataset.values,
        x=dataset.columns,
        y=dataset.index,
        colorscale='Viridis',
        hoverongaps=False
    ))

    fig.update_layout(
        xaxis_title='Columns',
        yaxis_title='Rows',
        title='Heatmap for Dataset'
    )
    st.markdown(f"""<h3 style="color:#7FFF00;">Heatmap of the Dataset</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig)


# Call the charts
def test_charts(files):
    test_data = get_suggestion(files, 20)  # Sample 20 rows from the CSV data

    display_charts(test_data)
    display_heatmap(test_data)

import numpy as np
import pandas as pd
import tensorflow as tf
import pickle

# Load the trained scaler and model
try:
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    model = tf.keras.models.load_model("diet_ann_model.h5")
except FileNotFoundError:
    print("❌ Error: Scaler or Model not found. Train them first.")
    scaler = None
    model = None



def recommend_diet(age, height, weight, activity_level):
    # ✅ Convert activity level to numeric
    activity_mapping = {
        "Little/no exercise": 1.2,
        "Light exercise": 1.375,
        "Moderate exercise (3-5 days/wk)": 1.55,
        "Very active (6-7 days/wk)": 1.725,
        "Extra active (very active & physical job)": 1.9
    }
    activity_value = activity_mapping.get(activity_level, 1.2)

    # ✅ Ensure input is DataFrame
    user_input = pd.DataFrame([[age, height, weight, activity_value]], columns=['Age', 'Height', 'Weight', 'Activity'])

    # ✅ Scale input
    user_input_scaled = scaler.transform(user_input)

    # ✅ Get predictions
    predicted_values = model.predict(user_input_scaled)[0]
    calories, carbs, fat, protein = np.nan_to_num(predicted_values, nan=0.0)
    # Fetch meal suggestions based on predicted calories
    recommended_meals = df[
        (df["Calories"].notna()) &  # Ensure Calories column has valid numbers
        (df["Calories"] >= calories - 200) &
        (df["Calories"] <= calories + 200)
        ]
    return {
        "Calories": round(calories) if not np.isnan(calories) else 0,
        "Carbs": round(carbs) if not np.isnan(carbs) else 0,
        "Fat": round(fat) if not np.isnan(fat) else 0,
        "Protein": round(protein) if not np.isnan(protein) else 0,
        "Meals": recommended_meals.sample(3)[
            ["Dish Name", "Calories", "Carbs", "Fat", "Protein", "Ingredients", "Instructions"]
        ].to_dict(orient="records") if not recommended_meals.empty else []
    }
#Display Menu
def display_menu():
    st.title('Custom Diet Recommendations')
    display = Display()
    files = load_data("dish_data.csv") # Load CSV data
    age = st.number_input('Age', min_value=2, max_value=80, step=1)
    height = st.number_input('Height(cm)', min_value=50, max_value=300, step=1)
    weight = st.number_input('Weight(Kg)', min_value=10, max_value=300, step=1)
    gender = st.radio('Gender', ('Male', 'Female'))
    activity = st.select_slider('Activity', options=['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)'])
    option = st.selectbox('Choose your weight loss plan:', display.plans)

    weight_loss = display.weights[display.plans.index(option)]

    number_of_meals = st.slider('Meals per day', min_value=3, max_value=5, step=1, value=3)

    generated = st.button('Recommend')

    if generated:
        person = Person(age, height, weight, gender, activity, weight_loss)

        # Get recommendations from the CSV data
        #health_data_files = get_suggestion(files, number_of_meals)
        #health_data_files[['Calories', 'Carbs', 'Fat', 'Protein']] = health_data_files['Nutrition (Calories;Carbs;Fat;Protein)'].str.split(';', expand=True)
        #Convert Calories to numeric (if needed)
        #health_data_files['Calories'] = pd.to_numeric(health_data_files['Calories'], errors='coerce')
        # Call ANN-based diet recommendation instead of get_suggestion()
        results = recommend_diet(age, height, weight, activity)
        # Convert recommended meals to DataFrame format for visualization
        # Ensure results is a dictionary with "Meals" key
        if "Error" in results:
            st.error(f"Error: {results['Error']}")
            return  # Stop execution if there's an error

        if isinstance(results.get("Meals", []), list):
            health_data_files = pd.DataFrame(results["Meals"])
        else:
            health_data_files = pd.DataFrame()  # Empty DataFrame to prevent crash
        #health_data_files = pd.DataFrame(results["Meals"])
        display.display_bmi(person)
        display.display_calories(person)
        display_recommendation(health_data_files)
        test_charts(files)


# Main app
def diet():
    display_menu()


if __name__ == '__main__':
    diet()
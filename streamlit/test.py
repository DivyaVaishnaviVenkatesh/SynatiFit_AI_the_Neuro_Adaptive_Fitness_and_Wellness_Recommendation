import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3

# Function to initialize a database for medicine data
def insert_medicine_data(username, disease_name, medicine_name, dosage_form, strength, instructions):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO medicines (username, disease_name, medicine_name, dosage_form, strength, instructions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, disease_name, medicine_name, dosage_form, strength, instructions))
        conn.commit()
        print(f"Inserted medicine data: Username={username}, Disease={disease_name}, Medicine={medicine_name}, Dosage Form={dosage_form}, Strength={strength}, Instructions={instructions}")
    except sqlite3.Error as e:
        print(f"Error inserting medicine data: {e}")
    finally:
        conn.close()

def fetch_medicines(username):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM medicines WHERE username = ?', (username,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_username():
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users LIMIT 1")  # Modify query if needed
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Medicine JSON File
medicine_data = '''
    {
        "diseases":[
            {
                "name":"Cold",
                "patients":45123332,
                "medicines":[
                    {
                        "name":"Ibuprofen",
                        "dosage_form":"Tablet",
                        "strength":"200 mg",
                        "instructions":"Take 1 tablet every 6-8 hours"
                    },
                    {
                        "name":"Acataminophen",
                        "dosage_form":"Capsule",
                        "strength":"500 mg",
                        "instructions":"Take 1 tablet every 4-6 hours"
                    },
                    {
                        "name":"Phenylephrine",
                        "dosage_form":"Syrup",
                        "strength":"5 mg/5 ml",
                        "instructions":"Take 10 ml every 4 hours"
                    }
                ]
            },
            {
                "name":"Hypertension",
                "patients":90763630,
                "medicines":[
                    {
                        "name":"Lisinopril",
                        "dosage_form":"Tablet",
                        "strength":"10 mg",
                        "instructions":"Take 1 tablet daily in the morning"
                    },
                    {
                        "name":"Amlodipine",
                        "dosage_form":"Tablet",
                        "strength":"5 mg",
                        "instructions":"Take 1 tablet daily in the morning"
                    },
                    {
                        "name":"Hydrochlorothiazide",
                        "dosage_form":"Capsule",
                        "strength":"25 mg",
                        "instructions":"Take 1 tablet daily in the morning"
                    }
                ]
            },
            {
                "name":"Diabetes",
                "patients":16783800,
                "medicines":[
                    {
                        "name":"Metformin",
                        "dosage_form":"Tablet",
                        "strength":"500 mg",
                        "instructions":"Take 1 tablet twice daily with meals"
                    },
                    {
                        "name":"Insulin (Rapid Acting)",
                        "dosage_form":"Injection",
                        "strength":"100 units/ml",
                        "instructions":"Take 8 units twice in the morning and evening"
                    },
                    {
                        "name":"Gliclazide",
                        "dosage_form":"Tablet",
                        "strength":"80 mg",
                        "instructions":"Take 1 tablet before breakfast"
                    }
                ]
            },
            {
                "name":"Flu",
                "patients":508580,
                "medicines":[
                    {
                        "name":"Oseltamivir",
                        "dosage_form":"Capsule",
                        "strength":"75 mg",
                        "instructions":"Take 1 capsule twice daily for 5 days"
                    },
                    {
                        "name":"Ibuprofen",
                        "dosage_form":"Tablet",
                        "strength":"400 mg",
                        "instructions":"Take 1 tablet every 6-8 hours for 5 days"
                    },
                    {
                        "name":"Acataminophen",
                        "dosage_form":"Syrup",
                        "strength":"160 mg/5 ml",
                        "instructions":"Take 10ml every 4-6 hours as needed for fever"
                    }
                ]
            },
            {
                "name":"Asthma",
                "patients":12464700,
                "medicines":[
                    {
                        "name":"Albuterol",
                        "dosage_form":"Inhaler",
                        "strength":"100 mcg",
                        "instructions":"Inhale 2 puffs every 4-6 hours"
                    },
                    {
                        "name":"Fluticasone",
                        "dosage_form":"Inhaler",
                        "strength":"50 mcg",
                        "instructions":"Take 1-2 puffs twice daily"
                    },
                    {
                        "name":"Montelukast",
                        "dosage_form":"Tablet",
                        "strength":"10 mg",
                        "instructions":"Take 1 tablet daily in the evening"
                    }
                ]
            }
        ]
    }
'''

def get_medicines(disease):
    data = json.loads(medicine_data)
    for entry in data["diseases"]:
        if entry["name"].lower() == disease.lower():
            return entry["medicines"]
    return None

def count_patients(medicine_data):
    dataset = json.loads(medicine_data)
    data = {"Disease": [], "Patient": []}
    for entry in dataset["diseases"]:
        data["Disease"].append(entry["name"])
        data["Patient"].append(entry["patients"])
    return pd.DataFrame(data)

def draw():
    df = count_patients(medicine_data)
    mean_of_patients = df["Patient"].mean()

    st.markdown(
        f"""
            <h2 style="color:lightblue;">Medicines Visualization</h2>
        """
        , unsafe_allow_html=True)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=df["Disease"], y=df["Patient"], marker_color='MediumPurple'))
    fig_bar.add_shape(
        type="line",
        x0=-0.5,
        y0=mean_of_patients,
        x1=len(df) - 0.5,
        y1=mean_of_patients,
        line=dict(color="red", dash="dash")
    )
    fig_bar.update_layout(
        title="Number of Patients per Diseases",
        xaxis_title="Diseases",
        yaxis_title="Number of Patients"
    )
    st.plotly_chart(fig_bar)

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df["Disease"], y=df["Patient"], mode='lines+markers', fill='tozeroy'))
    fig_line.update_layout(
        title="Trend of Number of Patients over diseases",
        xaxis_title="Diseases",
        yaxis_title="Number of Patients"
    )
    st.plotly_chart(fig_line)

def main_1():
    username = get_username()
    if not username:
        st.error("No user found in the database!")
        return  # Stop execution if no user is found
    st.title("Medication Recommender For Diseases")
    Age = st.selectbox('Age', ['Select', '10-18', '19-30', '31-50', 'Above 50'])
    disease_input = st.selectbox('Choose your disease', ['Select', 'Asthma', 'Cold', 'Diabetes', 'Flu', 'Hypertension'])

    if st.button("Recommend Medicines"):
        if Age == 'Select' or disease_input == 'Select':
            st.warning('Input Error!! Check the input fields')
        else:
            nums = 1
            medicines = get_medicines(disease_input)
            if medicines:
                st.markdown(f"""
                        <h4 style="font-style:italic; font-family:cursive;"> Suggested Medicines for {disease_input} are:</h4>
                    """,
                    unsafe_allow_html=True)
                for med in medicines:
                    insert_medicine_data(username,disease_input, med['name'], med['dosage_form'], med['strength'], med['instructions'])
                    st.markdown(
                        f"""
                            <h6 style="color:yellow;font-style:italic; font-family:cursive;">S.No: {nums}</h6>
                            <div class="medicine">
                                <p class="medicine-name" style="color:#7FFF00; font-style:italic; font-family:cursive;">{med['name']}</p>
                                <div class="medicine-details">
                                    <p style="color:#7FFF00; font-style:italic; font-family:cursive;">Dosage Form: {med['dosage_form']}</p>
                                    <p style="color:#7FFF00; font-style:italic; font-family:cursive;">Strength: {med['strength']}</p>
                                    <p style="color:#7FFF00; font-style:italic; font-family:cursive;">Instruction: {med['instructions']}</p>
                                </div>
                            </div>
                        """,
                        unsafe_allow_html=True)
                    nums += 1
                draw()

if __name__ == "__main__":
    main_1()
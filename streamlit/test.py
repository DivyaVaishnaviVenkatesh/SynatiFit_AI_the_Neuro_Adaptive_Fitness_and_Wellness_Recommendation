import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime
import PyPDF2
import io
import re
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import numpy as np

# Function to initialize a database for medicine data
def init_db():
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            disease_name TEXT,
            medicine_name TEXT,
            dosage_form TEXT,
            strength TEXT,
            instructions TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            log_type TEXT,
            value REAL,
            notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_health_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            issue_name TEXT,
            severity TEXT,
            notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Initialize database when module loads

def get_username():
    """Get the currently logged in username from session state"""
    if 'username' in st.session_state:
        return st.session_state.username
    return None

def get_medicines(disease):
    """Get recommended medicines for a specific disease from the JSON data"""
    try:
        data = json.loads(medicine_data)
        for entry in data["diseases"]:
            if entry["name"].lower() == disease.lower():
                return entry.get("medicines", [])
        return None
    except json.JSONDecodeError:
        st.error("Error loading medicine data")
        return None

def fetch_health_logs(username, log_type=None):
    """Fetch health logs from database for a specific user"""
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    
    if log_type:
        cursor.execute(
            'SELECT * FROM health_logs WHERE username = ? AND log_type = ? ORDER BY timestamp DESC',
            (username, log_type))
    else:
        cursor.execute(
            'SELECT * FROM health_logs WHERE username = ? ORDER BY timestamp DESC',
            (username,))
    
    data = cursor.fetchall()
    conn.close()
    return data

def insert_health_issue(username, issue_name, severity, notes):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_health_issues (username, issue_name, severity, notes)
            VALUES (?, ?, ?, ?)
        ''', (username, issue_name, severity, notes))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting health issue: {e}")
    finally:
        conn.close()

def fetch_medicines(username):
    """Fetch all medicines for a specific user from the database"""
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(medicines)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'timestamp' in columns:
            cursor.execute(
                'SELECT * FROM medicines WHERE username = ? ORDER BY timestamp DESC',
                (username,))
        else:
            cursor.execute(
                'SELECT * FROM medicines WHERE username = ?',
                (username,))
        
        data = cursor.fetchall()
        return data
        
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        conn.close()

def insert_medicine_data(username, disease_name, medicine_name, dosage_form, strength, instructions):
    """Insert medicine data into the database"""
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO medicines (username, disease_name, medicine_name, dosage_form, strength, instructions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, disease_name, medicine_name, dosage_form, strength, instructions))
        conn.commit()
        st.success(f"Successfully recorded {medicine_name} for {disease_name}")
    except sqlite3.Error as e:
        st.error(f"Error saving medicine data: {e}")
    finally:
        conn.close()

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
                        "name":"Acetaminophen",
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
                        "name":"Acetaminophen",
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

def fetch_health_issues(username):
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_health_issues WHERE username = ? ORDER BY timestamp DESC', (username,))
    data = cursor.fetchall()
    conn.close()
    return data

def analyze_basic_metrics(health_data):
    """Analyze and display basic health metrics with visualizations"""
    st.subheader("📊 Basic Health Metrics Analysis")
    
    if not health_data:
        st.warning("No health data provided")
        return
    
    # BMI Analysis
    if "weight" in health_data and health_data["weight"] and "height" in health_data and health_data["height"]:
        try:
            weight = float(health_data["weight"])
            height = float(health_data["height"]) / 100  # convert cm to meters
            
            bmi = weight / (height ** 2)
            bmi_category = (
                "Underweight" if bmi < 18.5
                else "Normal weight" if 18.5 <= bmi < 25
                else "Overweight" if 25 <= bmi < 30
                else "Obese"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Height", f"{health_data['height']} cm")
                st.metric("Weight", f"{weight} kg")
                st.metric("BMI", f"{bmi:.1f}")
                st.write(f"**Classification:** {bmi_category}")
            
            with col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=bmi,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "BMI"},
                    gauge={
                        'axis': {'range': [10, 40]},
                        'steps': [
                            {'range': [10, 18.5], 'color': "lightblue"},
                            {'range': [18.5, 25], 'color': "green"},
                            {'range': [25, 30], 'color': "orange"},
                            {'range': [30, 40], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': bmi
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
        except (ValueError, TypeError) as e:
            st.error(f"Error calculating BMI: {e}")
    
    # Blood Pressure Analysis
    if "bp" in health_data and health_data["bp"] is not None:
        try:
            bp = health_data["bp"]
            
            # Skip if BP is None or not in "XXX/YY" format
            if bp is None or not isinstance(bp, str) or "/" not in bp:
                st.warning("Blood pressure data missing or invalid format (expected 'SYS/DIA').")
                return
            
            systolic, diastolic = map(int, bp.split('/'))
            
            bp_category = (
                "Normal" if systolic < 120 and diastolic < 80
                else "Elevated" if 120 <= systolic < 130 and diastolic < 80
                else "High (Stage 1)" if 130 <= systolic < 140 or 80 <= diastolic < 90
                else "High (Stage 2)" if systolic >= 140 or diastolic >= 90
                else "Hypertensive Crisis"
            )
            
            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Blood Pressure", f"{systolic}/{diastolic} mmHg")
                st.write(f"**Classification:** {bp_category}")
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=['Systolic', 'Diastolic'],
                    y=[systolic, diastolic],
                    mode='markers+text',
                    marker=dict(size=30, color=['red', 'blue']),
                    text=[str(systolic), str(diastolic)],
                    textposition='top center'
                ))
                fig.update_layout(
                    title="Blood Pressure Readings",
                    yaxis_title="mmHg",
                    shapes=[
                        dict(type="line", yref="y", y0=120, y1=120, xref="paper", x0=0, x1=1),
                        dict(type="line", yref="y", y0=80, y1=80, xref="paper", x0=0, x1=1)
                    ]
                )
                st.plotly_chart(fig, use_container_width=True)
        except (ValueError, AttributeError) as e:
            st.error(f"Error analyzing blood pressure: Invalid format. Expected 'SYS/DIA' (e.g., '120/80').")
    else:
        st.warning("Blood pressure data not provided or invalid.")

def generate_recommendations(health_data):
    """Generate personalized health recommendations"""
    st.subheader("💡 Personalized Recommendations")
    
    if not health_data:
        st.warning("No health data available for recommendations")
        return
    
    # Nutrition recommendations
    st.write("### 🥗 Nutrition Plan")
    if "weight" in health_data and "height" in health_data:
        try:
            bmi = float(health_data["weight"]) / ((float(health_data["height"])/100) ** 2)
            if bmi > 25:
                st.write("- Reduce calorie intake by 300-500 calories/day")
                st.write("- Focus on whole foods and vegetables")
            elif bmi < 18.5:
                st.write("- Increase calorie intake with nutrient-dense foods")
            else:
                st.write("- Maintain balanced diet with proper portions")
        except:
            st.write("- Balanced diet with variety of whole foods")
    
    # Exercise recommendations
    st.write("### 🏋️ Exercise Plan")
    if "bp" in health_data and health_data["bp"]:
        systolic, diastolic = map(int, health_data["bp"].split('/'))
        if systolic >= 130 or diastolic >= 85:
            st.write("- 30 minutes moderate exercise daily (walking, swimming)")
            st.write("- Avoid heavy weight lifting")
        else:
            st.write("- 150 minutes moderate exercise weekly")
            st.write("- Strength training 2-3 times weekly")
    
    # Monitoring recommendations
    st.write("### 🩺 Health Monitoring")
    if "bp" in health_data and health_data["bp"]:
        systolic, diastolic = map(int, health_data["bp"].split('/'))
        if systolic >= 130 or diastolic >= 85:
            st.write("- Monitor blood pressure twice daily")
    st.write("- Annual health checkup recommended")

def extract_text_from_pdf(uploaded_file):
    """Extract text content from PDF"""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
    return "\n".join([page.extract_text() for page in pdf_reader.pages])

def extract_health_metrics(text):
    """Extract health metrics from text using precise regex patterns"""
    def extract_value(text, pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    metrics = {
        "weight": None,
        "height": None,
        "bp": None,
        "glucose": None,
        "cholesterol": None,
        "age": None,
        "issues": []
    }
    
    # Weight extraction (kg only)
    weight_match = re.search(r"Weight[:]?\s*(\d+)\s*(kg|kgs)\b", text, re.IGNORECASE)
    if weight_match:
        metrics["weight"] = weight_match.group(1)
    
    # Height extraction - prioritize cm in parentheses
    height_match = re.search(r"Height[:]?\s*(\d+)(?:['′](\d+))?[\"″]?\s*(?:\((\d+)\s*cm\)|cm)?", text, re.IGNORECASE)
    if height_match:
        if height_match.group(3):  # (175 cm) format
            metrics["height"] = float(height_match.group(3))
        elif height_match.group(1) and height_match.group(2):  # 5'9" format
            metrics["height"] = (float(height_match.group(1)) * 12 + float(height_match.group(2))) * 2.54
        elif height_match.group(1):  # Just cm
            metrics["height"] = float(height_match.group(1))
    
    # Blood pressure
    bp_match = re.search(r"Blood\s*Pressure[:]?\s*(\d+)\s*/\s*(\d+)", text, re.IGNORECASE)
    if bp_match:
        metrics["bp"] = f"{bp_match.group(1)}/{bp_match.group(2)}"
    
    # Glucose
    glucose_match = re.search(r"(?:Blood\s*Sugar|Glucose)[:]?\s*(\d+)", text, re.IGNORECASE)
    if glucose_match:
        metrics["glucose"] = glucose_match.group(1)
    
    # Cholesterol
    cholesterol_match = re.search(r"Cholesterol[:]?\s*(\d+)", text, re.IGNORECASE)
    if cholesterol_match:
        metrics["cholesterol"] = cholesterol_match.group(1)
    
    # Age
    age_match = re.search(r"Age[:]?\s*(\d+)", text, re.IGNORECASE)
    if age_match:
        metrics["age"] = age_match.group(1)
    
    # Health issues (from diagnosis)
    if "Hypertension" in text:
        metrics["issues"].append("Hypertension")
    
    # Remove duplicate issues
    metrics["issues"] = list(set(metrics["issues"]))
    
    return metrics

def count_patients(medicine_data):
    """Count patients for each disease from the medicine data"""
    try:
        data = json.loads(medicine_data)
        diseases = []
        patients = []
        
        for entry in data["diseases"]:
            diseases.append(entry["name"])
            patients.append(entry["patients"])
        
        return pd.DataFrame({
            "Disease": diseases,
            "Patient": patients
        })
    except json.JSONDecodeError:
        st.error("Error processing medicine data")
        return pd.DataFrame()


def show_enhanced_health_tracker():
    st.title("🏥 Comprehensive Health Analyzer")
    
    input_method = st.radio("How would you like to provide your health data?", 
                          ["📝 Manual Input", "📁 Upload Health Report (PDF)"])
    
    health_data = None
    
    if input_method == "📁 Upload Health Report (PDF)":
        st.subheader("Upload Your Health Report")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            try:
                text = extract_text_from_pdf(uploaded_file)
                health_data = extract_health_metrics(text)
                if health_data:
                    # Show the extracted data for verification
                    st.subheader("Extracted Health Data")
                    st.json(health_data)
                    
                    # Analyze and show recommendations
                    analyze_basic_metrics(health_data)
                    generate_recommendations(health_data)
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
    
    else:  # Manual Input
        st.subheader("Enter Your Health Metrics")
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            age = st.number_input("Age", min_value=10, max_value=100, value=30)
        with col2:
            bp_systolic = st.number_input("Blood Pressure (Systolic)", min_value=70, max_value=200, value=120)
            bp_diastolic = st.number_input("Blood Pressure (Diastolic)", min_value=40, max_value=120, value=80)
            glucose = st.number_input("Glucose Level (mg/dL)", min_value=50, max_value=300, value=90)
        
        if st.button("Analyze & Get Recommendations"):
            health_data = {
                "weight": weight,
                "height": height,
                "bp": f"{bp_systolic}/{bp_diastolic}",
                "glucose": glucose,
                "age": age,
                "issues": []
            }
            analyze_basic_metrics(health_data)
            generate_recommendations(health_data)

def draw():
    df = count_patients(medicine_data)
    mean_of_patients = df["Patient"].mean()

    st.markdown(
        f"""
            <h2 style="color:lightblue;">Medicines Visualization</h2>
        """
        , unsafe_allow_html=True)

    # Create unique keys using a timestamp
    timestamp = str(datetime.now().timestamp()).replace('.','')
    
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
    st.plotly_chart(fig_bar, key=f"patients_bar_{timestamp}")

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df["Disease"], y=df["Patient"], mode='lines+markers', fill='tozeroy'))
    fig_line.update_layout(
        title="Trend of Number of Patients over diseases",
        xaxis_title="Diseases",
        yaxis_title="Number of Patients"
    )
    st.plotly_chart(fig_line, key=f"patients_line_{timestamp}")

def main():
    if not st.session_state.get('logged_in', False):
        st.error("Please log in to access this feature")
        return
    
    username = st.session_state.username
    
    st.title("Health & Medication Management")
    
    tab1, tab2 = st.tabs(["Health Analyzer", "Medicine Recommender"])
    
    with tab1:
        show_enhanced_health_tracker()
    
    with tab2:
        st.header("Medication Recommender For Diseases")
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
                        insert_medicine_data(username, disease_input, med['name'], med['dosage_form'], med['strength'], med['instructions'])
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
    main()
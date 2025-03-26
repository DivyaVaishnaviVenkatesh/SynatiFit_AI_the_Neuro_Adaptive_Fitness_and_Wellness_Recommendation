import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import LabelEncoder
import pickle
from sklearn.preprocessing import StandardScaler

# 🚀 Load Dataset
def load_data(csv_file):
    return pd.read_csv(csv_file)
df = load_data("dish_data.csv")  # Ensure this file exists

# 🔹 Fix: Split Nutrition into Individual Columns
df[['Calories', 'Carbs', 'Fat', 'Protein']] = df['Nutrition (Calories;Carbs;Fat;Protein)'].str.split(';', expand=True)
df['Calories'] = pd.to_numeric(df['Calories'], errors='coerce')
df['Carbs'] = pd.to_numeric(df['Carbs'], errors='coerce')
df['Fat'] = pd.to_numeric(df['Fat'], errors='coerce')
df['Protein'] = pd.to_numeric(df['Protein'], errors='coerce')

# 🔹 Fix: Encode Dish Names (Target Variable)
label_encoder = LabelEncoder()
df['Dish_Label'] = label_encoder.fit_transform(df['Dish Name'])  # Convert dish names to numbers

# 🚀 Select Features (X) and Target (y)
X = df[['Calories', 'Carbs', 'Fat', 'Protein']]
y = df['Dish_Label']  # Encoded labels

# 🚀 Build ANN Model for Regression
model = Sequential([
    Dense(64, activation='relu', input_shape=(X.shape[1],)),
    Dense(32, activation='relu'),
    Dense(4, activation='linear')  # ✅ Output layer with 4 neurons for regression
])
# 🚀 Compile Model for Regression
model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # ✅ Use 'mse' for regression
# 🚀 Train Model
model.fit(X, y, epochs=20, batch_size=8, verbose=1)

# 🔹 Save Model & Label Encoder
model.save("diet_ann_model.h5")
with open("label_encoder.pkl", "wb") as le_file:
    pickle.dump(label_encoder, le_file)



scaler = StandardScaler()
X = df[['Calories', 'Carbs', 'Fat', 'Protein']]  # ✅ Ensure X is a DataFrame
y = X.copy()  # ✅ Target is also Calories, Carbs, Fat, Protein

X_scaled = scaler.fit_transform(X)

# ✅ Save Scaler

with open("scaler.pkl", "wb") as scaler_file:
    pickle.dump(scaler, scaler_file)

print("✅ Diet Recommendation Model & Label Encoder saved successfully!")

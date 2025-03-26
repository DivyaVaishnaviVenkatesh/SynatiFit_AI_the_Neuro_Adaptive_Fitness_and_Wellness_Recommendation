import pickle
from genetic_model import genetic_algorithm  # Import from the correct module

# Save the model
with open("genetic_model.pkl", "wb") as model_file:
    pickle.dump(genetic_algorithm, model_file)

print("✅ Model saved successfully!")

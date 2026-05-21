import streamlit as st
import requests

API_URL = "http://localhost:8000/predict"

st.title("Insurance Premium Category Predictor")

st.markdown("Enter your details below:")

age = st.number_input("Age", min_value=1, max_value=120, value=30)
weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
height = st.number_input("Height (m)", min_value=0.1, max_value=2.5, value=1.75)
income_lpa = st.number_input("Income per annum (LPA)", min_value=0.0, value=5.0)
smoker = st.selectbox("Are you a Smoker?", options=[True, False])
city = st.text_input("City", value="Bangalore")
occupation = st.selectbox("Occupation", options=['government_job', 'private_job', 'retired', 'student', 'business']) 

if st.button("Predict"):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(API_URL, json=input_data)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicted Insurance Premium Category: {result['Predicted_Category']}")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Please ensure the backend server is running.")
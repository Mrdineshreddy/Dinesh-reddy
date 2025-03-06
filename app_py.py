# -*- coding: utf-8 -*-
"""app.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u79S--jM2we3k0HswknZO-SaWuM51nCT
"""

import subprocess

# Install required packages
subprocess.run(["pip", "install", "streamlit", "tensorflow", "opencv-python", "requests", "numpy", "matplotlib"])

streamlit
tensorflow
opencv-python
requests
numpy
matplotlib

import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
import cv2
import requests
import matplotlib.pyplot as plt

# Set page title and layout
st.set_page_config(page_title="Food Nutrition Estimator", layout="wide")

# Title of the app
st.title("🍏 Food Nutrition Estimator")
st.write("Upload an image of your food, and we'll estimate its calories and nutrition information!")

# Load the pre-trained MobileNetV2 model
@st.cache_resource
def load_model():
    return MobileNetV2(weights="imagenet")

model = load_model()

# Function to preprocess an image for the model
def preprocess_image(img):
    img = cv2.resize(img, (224, 224))  # Resize to MobileNetV2 input size
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    img = preprocess_input(img)  # Preprocess for MobileNetV2
    return img

# Function to predict the food item
def predict_food_item(img):
    img = preprocess_image(img)
    predictions = model.predict(img)
    decoded_predictions = decode_predictions(predictions, top=1)[0]  # Get top prediction
    return decoded_predictions[0][1]  # Return the predicted food item name

# Function to fetch nutrition information from USDA API
def get_nutrition_from_api(food_item, api_key):
    """
    Fetches nutrition information for a given food item using the USDA FoodData Central API.

    Parameters:
        food_item (str): The name of the food item to search for.
        api_key (str): Your USDA FoodData Central API key.

    Returns:
        dict: Nutrition information for the food item.
    """
    # Define the API endpoint
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_item}&api_key={api_key}"

    try:
        # Make the API request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # Check if any results were found
            if data.get("foods"):
                # Extract nutrition information from the first result
                food_info = data["foods"][0]
                nutrients = food_info.get("foodNutrients", [])

                # Create a dictionary to store nutrition information
                nutrition_info = {}
                for nutrient in nutrients:
                    nutrient_name = nutrient.get("nutrientName", "")
                    nutrient_value = nutrient.get("value", "")
                    nutrient_unit = nutrient.get("unitName", "")
                    if nutrient_name and nutrient_value:
                        nutrition_info[nutrient_name] = f"{nutrient_value} {nutrient_unit}"

                return nutrition_info
            else:
                return f"No nutrition information found for '{food_item}'."
        else:
            return f"Failed to fetch nutrition information. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

# Function to classify food as healthy or unhealthy
def classify_food_health(nutrition_info):
    """
    Classifies a food item as healthy or unhealthy based on its nutrition information.

    Parameters:
        nutrition_info (dict): Nutrition information for the food item.

    Returns:
        str: "Good for health" or "Not good for health".
    """
    # Extract relevant nutrition values
    calories = float(nutrition_info.get("Energy", "0 kcal").split()[0])
    fat = float(nutrition_info.get("Total lipid (fat)", "0 g").split()[0])
    fiber = float(nutrition_info.get("Fiber, total dietary", "0 g").split()[0])

    # Define health criteria
    if calories < 200 and fat < 10 and fiber > 2:
        return "Good for health"
    else:
        return "Not good for health"

# Upload image
uploaded_file = st.file_uploader(  "C:/Users/ASUS/Downloads/dinesh.ipynb", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Display the image
    st.image(img, channels="BGR", caption= "C:/Users/ASUS/Downloads/dinesh.ipynb", use_column_width=True)

    # Predict the food item
    food_item = predict_food_item(img)
    st.subheader(f"Predicted Food Item: {food_item}")

    # Fetch nutrition information
    api_key =  "olpFKY7JzxlSYuSOU7Per9LGVLyIzUwoIEXHrbnb"  # Replace with your USDA API key
    nutrition_info = get_nutrition_from_api(food_item, api_key)

    if isinstance(nutrition_info, dict):
        # Display nutrition information
        st.subheader("Nutrition Information:")
        for nutrient, value in nutrition_info.items():
            st.write(f"{nutrient}: {value}")

        # Extract and display calories
        calories = nutrition_info.get("Energy", "N/A")
        st.subheader(f"Calories: {calories}")

        # Classify food as healthy or unhealthy
        health_status = classify_food_health(nutrition_info)
        st.subheader(f"Health Status: {health_status}")
    else:
        st.error(nutrition_info)

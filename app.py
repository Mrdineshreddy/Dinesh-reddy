{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyOSoFiW7A+N8hJO0SxQO/Zu",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/Mrdineshreddy/Dinesh-reddy/blob/main/app.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "# -*- coding: utf-8 -*-\n",
        "\"\"\"app.py\n",
        "\n",
        "Food Nutrition Estimator using Streamlit and TensorFlow.\n",
        "\"\"\"\n",
        "\n",
        "import subprocess\n",
        "\n",
        "# Install required packages\n",
        "subprocess.run([\"pip\", \"install\", \"streamlit\", \"tensorflow\", \"opencv-python\", \"requests\", \"numpy\", \"matplotlib\"])\n",
        "\n",
        "import streamlit as st\n",
        "import tensorflow as tf\n",
        "from tensorflow.keras.applications import MobileNetV2\n",
        "from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions\n",
        "import numpy as np\n",
        "import cv2\n",
        "import requests\n",
        "import matplotlib.pyplot as plt\n",
        "\n",
        "# Set page title and layout\n",
        "st.set_page_config(page_title=\"Food Nutrition Estimator\", layout=\"wide\")\n",
        "\n",
        "# Title of the app\n",
        "st.title(\"🍏 Food Nutrition Estimator\")\n",
        "st.write(\"Upload an image of your food, and we'll estimate its calories and nutrition information!\")\n",
        "\n",
        "# Load the pre-trained MobileNetV2 model\n",
        "@st.cache_resource\n",
        "def load_model():\n",
        "    return MobileNetV2(weights=\"imagenet\")\n",
        "\n",
        "model = load_model()\n",
        "\n",
        "# Function to preprocess an image for the model\n",
        "def preprocess_image(img):\n",
        "    img = cv2.resize(img, (224, 224))  # Resize to MobileNetV2 input size\n",
        "    img = np.expand_dims(img, axis=0)  # Add batch dimension\n",
        "    img = preprocess_input(img)  # Preprocess for MobileNetV2\n",
        "    return img\n",
        "\n",
        "# Function to predict the food item\n",
        "def predict_food_item(img):\n",
        "    img = preprocess_image(img)\n",
        "    predictions = model.predict(img)\n",
        "    decoded_predictions = decode_predictions(predictions, top=1)[0]  # Get top prediction\n",
        "    return decoded_predictions[0][1]  # Return the predicted food item name\n",
        "\n",
        "# Function to fetch nutrition information from USDA API\n",
        "def get_nutrition_from_api(food_item, api_key):\n",
        "    \"\"\"\n",
        "    Fetches nutrition information for a given food item using the USDA FoodData Central API.\n",
        "\n",
        "    Parameters:\n",
        "        food_item (str): The name of the food item to search for.\n",
        "        api_key (str): Your USDA FoodData Central API key.\n",
        "\n",
        "    Returns:\n",
        "        dict: Nutrition information for the food item.\n",
        "    \"\"\"\n",
        "    # Define the API endpoint\n",
        "    url = f\"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_item}&api_key={api_key}\"\n",
        "\n",
        "    try:\n",
        "        # Make the API request\n",
        "        response = requests.get(url)\n",
        "\n",
        "        # Check if the request was successful\n",
        "        if response.status_code == 200:\n",
        "            data = response.json()\n",
        "\n",
        "            # Check if any results were found\n",
        "            if data.get(\"foods\"):\n",
        "                # Extract nutrition information from the first result\n",
        "                food_info = data[\"foods\"][0]\n",
        "                nutrients = food_info.get(\"foodNutrients\", [])\n",
        "\n",
        "                # Create a dictionary to store nutrition information\n",
        "                nutrition_info = {}\n",
        "                for nutrient in nutrients:\n",
        "                    nutrient_name = nutrient.get(\"nutrientName\", \"\")\n",
        "                    nutrient_value = nutrient.get(\"value\", \"\")\n",
        "                    nutrient_unit = nutrient.get(\"unitName\", \"\")\n",
        "                    if nutrient_name and nutrient_value:\n",
        "                        nutrition_info[nutrient_name] = f\"{nutrient_value} {nutrient_unit}\"\n",
        "\n",
        "                return nutrition_info\n",
        "            else:\n",
        "                return f\"No nutrition information found for '{food_item}'.\"\n",
        "        else:\n",
        "            return f\"Failed to fetch nutrition information. Status code: {response.status_code}\"\n",
        "    except Exception as e:\n",
        "        return f\"An error occurred: {e}\"\n",
        "\n",
        "# Function to classify food as healthy or unhealthy\n",
        "def classify_food_health(nutrition_info):\n",
        "    \"\"\"\n",
        "    Classifies a food item as healthy or unhealthy based on its nutrition information.\n",
        "\n",
        "    Parameters:\n",
        "        nutrition_info (dict): Nutrition information for the food item.\n",
        "\n",
        "    Returns:\n",
        "        str: \"Good for health\" or \"Not good for health\".\n",
        "    \"\"\"\n",
        "    # Extract relevant nutrition values\n",
        "    calories = float(nutrition_info.get(\"Energy\", \"0 kcal\").split()[0])\n",
        "    fat = float(nutrition_info.get(\"Total lipid (fat)\", \"0 g\").split()[0])\n",
        "    fiber = float(nutrition_info.get(\"Fiber, total dietary\", \"0 g\").split()[0])\n",
        "\n",
        "    # Define health criteria\n",
        "    if calories < 200 and fat < 10 and fiber > 2:\n",
        "        return \"Good for health\"\n",
        "    else:\n",
        "        return \"Not good for health\"\n",
        "\n",
        "# Upload image\n",
        "uploaded_file = st.file_uploader(\"C:/Users/ASUS/Downloads/dinesh.ipynb\", type=[\"jpg\", \"jpeg\", \"png\"])\n",
        "\n",
        "if uploaded_file is not None:\n",
        "    # Read the image\n",
        "    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)\n",
        "    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)\n",
        "\n",
        "    # Display the image\n",
        "    st.image(img, channels=\"BGR\", caption=\"Uploaded Image\", use_column_width=True)\n",
        "\n",
        "    # Predict the food item\n",
        "    food_item = predict_food_item(img)\n",
        "    st.subheader(f\"Predicted Food Item: {food_item}\")\n",
        "\n",
        "    # Fetch nutrition information\n",
        "    api_key = \"olpFKY7JzxlSYuSOU7Per9LGVLyIzUwoIEXHrbnb\"  # Replace with your USDA API key\n",
        "    nutrition_info = get_nutrition_from_api(food_item, api_key)\n",
        "\n",
        "    if isinstance(nutrition_info, dict):\n",
        "        # Display nutrition information\n",
        "        st.subheader(\"Nutrition Information:\")\n",
        "        for nutrient, value in nutrition_info.items():\n",
        "            st.write(f\"{nutrient}: {value}\")\n",
        "\n",
        "        # Extract and display calories\n",
        "        calories = nutrition_info.get(\"Energy\", \"N/A\")\n",
        "        st.subheader(f\"Calories: {calories}\")\n",
        "\n",
        "        # Classify food as healthy or unhealthy\n",
        "        health_status = classify_food_health(nutrition_info)\n",
        "        st.subheader(f\"Health Status: {health_status}\")\n",
        "    else:\n",
        "        st.error(nutrition_info)"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "il4HlFBUQ_a4",
        "outputId": "cd54cca8-90c4-4bc4-8e72-bdcf87317a37"
      },
      "execution_count": 17,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "2025-03-06 21:03:37.305 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.306 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.307 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.307 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.308 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.308 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.309 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.311 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.312 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.314 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.315 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
            "2025-03-06 21:03:37.316 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [],
      "metadata": {
        "id": "6iImMK6HRAY0"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
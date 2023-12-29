# modeling.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your KittyCAD API Key
KITTYCAD_API_TOKEN = os.getenv("KITTYCAD_API_TOKEN")
if not KITTYCAD_API_TOKEN:
    raise ValueError("Please set the KITTYCAD_API_TOKEN environment variable.")

# KittyCAD API endpoints
BASE_URL = "https://api.kittycad.io"
TEXT_TO_CAD_ENDPOINT = f"{BASE_URL}/ai/text-to-cad/{{output_format}}"

def text_to_cad(description: str, output_format: str):
    """
    Generates a CAD model from a text description using KittyCAD's AI.
    :param description: A text description of the object to be generated.
    :param output_format: The desired output CAD format (e.g., 'stl').
    :return: A URL to the generated CAD model, or None if there was an error.
    """
    headers = {
        "Authorization": f"Bearer {KITTYCAD_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "description": description
    }

    url = TEXT_TO_CAD_ENDPOINT.format(output_format=output_format)

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        if response.status_code == 200:
            # Assuming the API returns a URL to the generated model
            model_url = response.json().get("model_url")
            print(f"Model successfully generated. You can download it from: {model_url}")
            return model_url
        else:
            print(f"Failed to generate model. Status Code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred while generating the CAD model: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace 'Your CAD model description here' with an actual description
    model_url = text_to_cad("Your CAD model description here", "stl")
    if model_url:
        print("Generated model URL:", model_url)

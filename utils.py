import os
import io
import tempfile
import speech_recognition as sr
import pyvista as pv
from stpyvista import stpyvista
import streamlit as st
import cad_prompts
from openai_text import generate_ai_text
import logging
import time
import requests
from dotenv import load_dotenv
import base64

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()


KITTYCAD_API_TOKEN = os.getenv("KITTYCAD_API_TOKEN")
if not KITTYCAD_API_TOKEN:
    raise ValueError("Please set the KITTYCAD_API_TOKEN environment variable.")

# KittyCAD API endpoints
BASE_URL = "https://api.zoo.dev"
TEXT_TO_CAD_ENDPOINT = f"{BASE_URL}/ai/text-to-cad/{{output_format}}"
USER_TEXT_TO_CAD_STATUS_ENDPOINT = f"{BASE_URL}/user/text-to-cad/{{operation_id}}"

def text_to_cad(description: str, output_format: str):
    headers = {
        "Authorization": f"Bearer {KITTYCAD_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": description,
        "output_format": output_format
    }

    url = TEXT_TO_CAD_ENDPOINT.format(output_format=output_format)

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        if response.status_code == 201:
            operation_id = response.json().get("id")
            if operation_id:
                logging.info(f"Model generation initiated. Operation ID: {operation_id}")
                return operation_id
            else:
                logging.error("Received a 201 status but no operation ID was found in the response.")
                return None
        else:
            logging.error(f"Failed to initiate model generation. Status Code: {response.status_code}")
            logging.error(f"Error Message: {response.text}")
            return None

    except Exception as e:
        logging.exception(f"An error occurred while initiating the CAD model generation: {e}")
        return None

def decode_file_content(base64_content: str):
    # Fix padding if necessary
    base64_content += "=" * ((4 - len(base64_content) % 4) % 4)
    try:
        file_data = base64.b64decode(base64_content)
        logging.info("File content decoded successfully.")
        return file_data
    except base64.binascii.Error as e:
        logging.error(f"An error occurred while decoding the file content: {e}")
        return None

def check_model_generation_status(operation_id: str):
    headers = {
        "Authorization": f"Bearer {KITTYCAD_API_TOKEN}"
    }

    url = USER_TEXT_TO_CAD_STATUS_ENDPOINT.format(operation_id=operation_id)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.status_code == 200:
            operation_status = response.json().get("status")
            logging.info(f"Model generation status: {operation_status}")
            
            # Return decoded content when the operation is completed
            if operation_status == 'completed':
                outputs = response.json().get('outputs')
                decoded_contents = {}
                for file_name, base64_content in outputs.items():
                    file_data = decode_file_content(base64_content)
                    if file_data:
                        decoded_contents[file_name] = file_data
                return {"status": operation_status, "files": decoded_contents}
            return {"status": operation_status}
        else:
            logging.error(f"Failed to get model generation status. Status Code: {response.status_code}")
            logging.error(f"Error Message: {response.text}")
            return None

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP Error occurred: {http_err}")
        logging.error("Ensure the operation ID is correct and the endpoint is accessible.")
        logging.error(f"Operation ID being checked: {operation_id}")
    except Exception as e:
        logging.exception(f"An error occurred while checking the model generation status: {e}")
    finally:
        time.sleep(8)  # Avoid rapid polling



def generate_formatted_instructions(user_intent):
    try:
        instructions_prompt = cad_prompts.MANUFACTURING_INSTRUCTIONS.format(user_idea=user_intent)
        manufacturing_instructions = generate_ai_text(instructions_prompt, 0.808)
        formatted_prompt = cad_prompts.FORMATTED_INSTRUCTIONS.format(manufacturing_instructions=manufacturing_instructions)
        formatted_instructions = generate_ai_text(formatted_prompt, 0.808)
        return True, formatted_instructions
    except Exception as e:
        logging.exception("An error occurred during generating formatted instructions: {}".format(str(e)))
        return False, "An unexpected error occurred during the process."


def generate_stl_model(formatted_instructions):
    try:
        # Ensure only STL format is requested
        operation_id = text_to_cad(formatted_instructions, "stl")
        if not operation_id:
            return "Failed", "Failed to initiate model generation.", None

        # Poll for the model generation status
        while True:
            result = check_model_generation_status(operation_id)
            if result:
                model_status = result.get("status")
                if model_status == "completed":
                    # Filter the result to ensure only STL files are processed
                    stl_files = {k: v for k, v in result.get("files", {}).items() if k.endswith('.stl')}
                    return "Completed", stl_files
                elif model_status == "failed":
                    return "Failed", "Model generation failed."
            else:
                return "Failed", "Failed to check model generation status."
            time.sleep(5)
    except Exception as e:
        logging.exception("An error occurred during the STL generation process: {}".format(str(e)))
        return "Error", "An unexpected error occurred during the process."

def provide_download_button(stl_data_bytes, file_name="model.stl"):
    """
    Provides a download button for the STL file using Streamlit.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(stl_data_bytes)
        tmp.flush()
        tmp.seek(0)  # Go back to the beginning of the file to read its content
        tmp_bytes = tmp.read()  # Read the content as bytes

    st.download_button(label="Download STL", data=tmp_bytes, file_name=file_name, mime="model/stl")



def speech_to_text(audio_data):
    """
    Converts speech from in-memory audio data to text using Google's Speech Recognition API.
    """
    recognizer = sr.Recognizer()
    with io.BytesIO(audio_data) as audio_file:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"


def save_uploaded_file(uploaded_file):
    """
    Saves an uploaded file to a temporary file.

    :param uploaded_file: The uploaded file to save.
    :return: The path to the saved temporary file or None if saving fails.
    """
    try:
        # Create a temporary file with a suffix matching the uploaded file's extension
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='wb') as tmp:
            # Read the contents of the uploaded file and write them to the temporary file
            contents = uploaded_file.getvalue()
            tmp.write(contents)
            # Return the path to the temporary file
            return tmp.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None


def find_latest_stl(base_dir):
    """
    Finds the latest STL file in a given base directory.
    """
    subdirectories = [os.path.join(base_dir, d) for d in os.listdir(base_dir)
                      if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('output_')]
    if not subdirectories:
        return None
    latest_dir = max(subdirectories, key=os.path.getmtime)
    stl_files = [f for f in os.listdir(latest_dir) if f.endswith('.stl')]
    if not stl_files:
        return None
    latest_stl = max(stl_files, key=lambda f: os.path.getctime(os.path.join(latest_dir, f)))
    return os.path.join(latest_dir, latest_stl)

def visualize_stl(stl_data_bytes):
    """
    Visualizes an STL file using PyVista within Streamlit, directly from binary data.
    """
    if not isinstance(stl_data_bytes, bytes):
        st.error("STL data must be a bytes object.")
        return
    
    # Create a temporary file to save the STL data
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(stl_data_bytes)
        tmp.flush()  # Make sure data is written
        file_path = tmp.name  # Get the path of the temporary file

    try:
        pv.global_theme.allow_empty_mesh = True
        plotter = pv.Plotter(window_size=[500, 500])
        mesh = pv.read(file_path)
        plotter.add_mesh(mesh, color='white', show_edges=True)
        plotter.view_isometric()
        plotter.background_color = 'white'
        unique_key = f"pv_stl_{os.path.basename(file_path)}"  # Unique key based on file name
        # Use the stpyvista function to render PyVista plotter in Streamlit
        stpyvista(plotter, key=unique_key)  # Adjusted to match your successful past usage

    finally:
        os.remove(file_path)  # Ensure the temporary file is deleted after use

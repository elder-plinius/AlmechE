import streamlit as st
import pyvista as pv
import os
import io
import tempfile
import time
import speech_recognition as sr
from pydub import AudioSegment
from stpyvista import stpyvista
from openai_text import generate_ai_text
from modeling import text_to_cad, check_model_generation_status
from openai_vision import OpenAIVision
import cad_prompts

class Almeche:
    def __init__(self):
        self.vision_model = OpenAIVision() 
        self.STL_BASE_DIR = "C:/Users/Guest1/Desktop/AlmechE" 
# Function to find the latest STL file
    def find_latest_stl(self, base_dir):
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

    # Function to visualize STL file using stpyvista
    def visualize_stl(self, file_path):
        plotter = pv.Plotter(window_size=[400, 400])
        mesh = pv.read(file_path)
        plotter.add_mesh(mesh, color='white', show_edges=True)
        plotter.view_isometric()
        plotter.background_color = 'white'
        unique_key = f"pv_stl_{os.path.basename(file_path)}"  # Unique key based on file name
        stpyvista(plotter, key=unique_key)

    # Function to convert speech to text
    def speech_to_text(self, audio_file):
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

    def save_uploaded_file(self, uploaded_file):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                return tmp_file.name
        except Exception as e:
            st.error(f"Error saving file: {e}")
            return None

    # Main Streamlit interface layout
    def main(self):
        st.title('Welcome to AlmechE')
        st.write("Transform your ideas into tangible 3D printed objects.")

        # Initialize OpenAI Vision Model
        vision_model = OpenAIVision()

        # Input Method Selection
        st.header("Input Your Idea")
        idea_input_method = st.radio("Choose the input method for your idea:", ["Type Idea", "Speak Idea", "Upload Image"])

        idea = None
        user_intent = None
        image_analysis = ""

        if idea_input_method == "Type Idea":
            user_intent = st.text_area("Type your idea here:")
        elif idea_input_method == "Speak Idea":
            audio_file = st.file_uploader("Upload an audio file", type=['wav', 'mp3'])
            if audio_file is not None:
                if audio_file.type == "audio/mp3":
                    audio_file = io.BytesIO(AudioSegment.from_mp3(audio_file).export(format="wav"))
                user_intent = self.speech_to_text(audio_file)
                st.text_area("Your transcribed text:", value=user_intent, height=100)
        elif idea_input_method == "Upload Image":
            uploaded_image = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
            if uploaded_image is not None:
                # Display the uploaded image
                st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)

                temp_image_path = self.save_uploaded_file(uploaded_image)
                if temp_image_path:
                    image_analysis = vision_model.analyze_image(temp_image_path)
                    st.write("Image analysis:", image_analysis)
                    os.remove(temp_image_path)  # Clean up the temporary file
                user_intent = st.text_input("How're we using this image to make a 3D object? Are we cloning it, creating a fix for a broken part, a case or accessory? Please describe.")

        # Combine image analysis and user intent
        if image_analysis and user_intent:
            idea = f"{image_analysis} - User intends to: {user_intent}"
        elif user_intent:
            idea = user_intent

        # Process Idea Button
        if st.button("Generate 3D Model"):
            if idea:
                st.write("Processing your idea...")
                instructions_prompt = cad_prompts.MANUFACTURING_INSTRUCTIONS.format(user_idea=idea)
                manufacturing_instructions = generate_ai_text(instructions_prompt, 0.808)
                st.write(f"Manufacturing instructions: {manufacturing_instructions}")
                formatted_prompt = cad_prompts.FORMATTED_INSTRUCTIONS.format(manufacturing_instructions=manufacturing_instructions)
                formatted_instructions = generate_ai_text(formatted_prompt, 0.808)
                st.write(f"Formatted instructions: {formatted_instructions}")
                operation_id = text_to_cad(formatted_instructions, "stl")
                if operation_id:
                    st.write(f"Model generation initiated. Operation ID: {operation_id}")
                    while True:
                        result = check_model_generation_status(operation_id)
                        if result and result.get("status") == "completed":
                            st.success("Model generated successfully.")
                            STL_BASE_DIR = "C:/Users/Guest1/Desktop/AlmechE"
                            latest_stl_file = self.find_latest_stl(STL_BASE_DIR)
                            if latest_stl_file:
                                self.visualize_stl(latest_stl_file)
                            break
                        elif result and result.get("status") == "failed":
                            st.error("Model generation failed.")
                            break
                        time.sleep(1)
                else:
                    st.error("Failed to initiate model generation.")
            else:
                st.error("Please input an idea or upload an image to proceed.")

if __name__ == "__main__":
    almeche = Almeche()
    almeche.main()

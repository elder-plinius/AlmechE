# Import necessary libraries
import streamlit as st
import io
import os
from pydub import AudioSegment
import pyvista as pv
from openai_vision import OpenAIVision
from utils import provide_download_button, generate_formatted_instructions, generate_stl_model, speech_to_text, save_uploaded_file, visualize_stl

class Almeche:
    def __init__(self):
        self.vision_model = OpenAIVision()

    def main(self):
        st.title('Welcome to AlmechE')
        st.write("Transform your ideas into tangible 3D printed objects.")

        # Input Method Selection
        st.header("Input Your Idea")
        idea_input_method = st.radio(
            "Choose the input method for your idea:",
            ["Type Idea", "Speak Idea", "Upload Image"]
        )

        user_intent = ""
        if idea_input_method == "Type Idea":
            user_intent = st.text_area("Type your idea here:")

        elif idea_input_method == "Speak Idea":
            audio_file = st.file_uploader("Upload an audio file", type=['wav', 'mp3'])
            if audio_file is not None:
                audio_data = audio_file.read()
                if audio_file.type == "audio/mp3":
                    audio_data = AudioSegment.from_mp3(io.BytesIO(audio_data)).export(format="wav")
                user_intent = speech_to_text(io.BytesIO(audio_data))
                st.text_area("Your transcribed text:", value=user_intent, height=100)

        elif idea_input_method == "Upload Image":
            uploaded_image = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
            if uploaded_image is not None:
                st.image(uploaded_image, caption='Uploaded Image.', use_column_width=True)
                temp_image_path = save_uploaded_file(uploaded_image)
                if temp_image_path:
                    image_analysis = self.vision_model.analyze_image(temp_image_path)
                    st.write("Image analysis:", image_analysis)
                    additional_description = st.text_input("How're we using this image to make a 3D object? Please describe.")
                    os.remove(temp_image_path)  # Clean up the temporary file
            
                    if st.button("Generate 3D Model with Image"):
                        combined_idea = f"{image_analysis} - {additional_description}"
                        status, formatted_instructions = generate_formatted_instructions(combined_idea)
                        if status:
                            st.write("Formatted instructions based on image analysis and description:", formatted_instructions)
                            status, stl_files = generate_stl_model(formatted_instructions)
                            if status == "Completed":
                                st.success("Model generated successfully.")
                                for file_name, stl_data_bytes in stl_files.items():
                                    provide_download_button(stl_data_bytes, file_name)
                                    visualize_stl(stl_data_bytes)
                            else:
                                st.error("An error occurred: " + stl_files)
                        else:
                            st.error(formatted_instructions)

if __name__ == "__main__":
    Almeche().main()

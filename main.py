# main.py

import openai
import os
import cad_prompts

# Set your OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_ai_text(prompt: str, temperature: float) -> str:
    """
    Generates text based on a given prompt using OpenAI's GPT-4-1106-preview model.
    :param prompt: The prompt to feed into the AI model.
    :param temperature: Controls the randomness of the output (higher is more random).
    :return: The generated text.
    """
    try:
        response = openai.Completion.create(
            engine="gpt-4-1106-preview",  # Specify the GPT-4-1106-preview model
            prompt=prompt,
            max_tokens=150,  # Adjust based on your needs
            n=1,
            stop=None,
            temperature=temperature  # Adjust for creativity. Lower is more deterministic.
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error generating text."

def main(use_ai_for_idea: bool):
    # Initial idea generation
    if use_ai_for_idea:
        # AI generates an initial idea
        idea = generate_ai_text(cad_prompts.IDEA_GENERATION['prompt'], cad_prompts.IDEA_GENERATION['temperature'])
        print("AI-Generated Idea:", idea)
    else:
        # User provides the initial idea
        idea = input("Enter your innovative idea: ")
        print("User-Provided Idea:", idea)
    
    # Regardless of the initial idea source, the rest of the system is autonomous
    
    # AI helps in design planning
    design_plan = generate_ai_text(cad_prompts.DESIGN_PLANNING['prompt'], cad_prompts.DESIGN_PLANNING['temperature'])
    print("Design Plan:", design_plan)
    
    # AI develops technical specifications
    technical_specs = generate_ai_text(cad_prompts.TECHNICAL_SPECIFICATION['prompt'], cad_prompts.TECHNICAL_SPECIFICATION['temperature'])
    print("Technical Specifications:", technical_specs)
    
    # AI creates manufacturing instructions
    manufacturing_instructions = generate_ai_text(cad_prompts.MANUFACTURING_INSTRUCTIONS['prompt'], cad_prompts.MANUFACTURING_INSTRUCTIONS['temperature'])
    print("Manufacturing Instructions:", manufacturing_instructions)

if __name__ == "__main__":
    USE_AI_FOR_IDEA = True  # Set to False to input your own idea
    main(USE_AI_FOR_IDEA)

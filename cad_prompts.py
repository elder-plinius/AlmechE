# cad_prompts.py

# Prompt and temperature for generating innovative product ideas
IDEA_GENERATION = {
    'prompt': """
    Consider the latest trends in the specified industry and generate innovative product ideas. 
    Think about how new technologies can solve existing problems or create new opportunities.
    """,
    'temperature': 0.7  # adjust as needed
}

# Prompt and temperature for creating preliminary design plans
DESIGN_PLANNING = {
    'prompt': """
    Create a preliminary design plan for the selected product idea. 
    Detail the required components, their functions, and how they will interact. 
    Consider aspects such as materials, durability, and user experience in your plan.
    """,
    'temperature': 0.6  # adjust as needed
}

# Prompt and temperature for developing detailed technical specifications
TECHNICAL_SPECIFICATION = {
    'prompt': """
    Develop detailed technical specifications for the product's components. 
    Include information on materials, dimensions, tolerances, and manufacturing requirements. 
    Ensure all specifications meet industry standards and safety regulations.
    """,
    'temperature': 0.5  # adjust as needed
}

# Prompt and temperature for creating manufacturing instructions based on technical specifications
MANUFACTURING_INSTRUCTIONS = {
    'prompt': """
    Create detailed manufacturing instructions based on the provided technical specifications. 
    Guide the manufacturing process step-by-step, ensuring precision and adherence to the specified requirements.
    """,
    'temperature': 0.4  # adjust as needed
}

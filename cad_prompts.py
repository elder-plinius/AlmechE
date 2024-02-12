# cad_prompts.py

# Prompt for generating innovative product ideas
IDEA_GENERATION = """
Generate simple-to-manufacture yet highly innovative and uniquely designed CAD object ideas.
Think about how to simply address existing real-world problems, design something fun or beautiful, or create new opportunities in a unique way.
Provide a concise description of the most promising idea that we can 3D print.
Keep your response under 20 words.
"""

MANUFACTURING_INSTRUCTIONS = """
Based on the idea '{user_idea}', provide structured instructions suitable for 3D CAD modeling.
Craft a detailed and concise description that includes specific dimensions, geometric properties, negative space 
(openings, holes, hollowness, recesses, etc.), and other relevant features.
If the concept is too complex for a single print, instead come up with a clever design the best possible version of a simplified Minimum Viable Product (MVP).
Aim for a design that is as minimalist a possible. Explain the design in specific, unambiguous terms as if to describe it to a novice Mechanical Engineer
that has never seen this object before. Keep your response concise and under 80 words.
"""

FORMATTED_INSTRUCTIONS = """
Generate concise, well-formatted 3D modeling instructions for generating a 3D CAD object based on our preliminary manufacturing instructions: '{manufacturing_instructions}'.
Be sure to include dimensions and be descriptive of the object's geometry and how exactly each shape fits together, like you're explaining the object to a young Mechanical Engineer's AI text-to-CAD LLM who has never seen this object type before.
Adjust the format and details as needed for the specific object being designed and keep your response under 58 words.
"""

# streamlit_app.py

import os
import streamlit as st
import pygame
import numpy as np
from render import parse_syntax, render_whiteboard
from gpt import GPTWhiteboardGenerator
from dotenv import load_dotenv
from PIL import Image

# Set the SDL_VIDEODRIVER environment variable to 'dummy' to prevent Pygame from opening a window
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Initialize Pygame
pygame.init()

# Load environment variables and API key
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the GPTWhiteboardGenerator with the API key
generator = GPTWhiteboardGenerator(API_KEY)

def surface_to_image(surface):
    """Converts a Pygame surface to a PIL image."""
    data = pygame.image.tostring(surface, 'RGBA')
    image = Image.frombytes('RGBA', surface.get_size(), data)
    return image

# Initialize session state variables
if 'problem_description' not in st.session_state:
    st.session_state.problem_description = ''
if 'whiteboard_syntax' not in st.session_state:
    st.session_state.whiteboard_syntax = ''
if 'elements' not in st.session_state:
    st.session_state.elements = []
if 'content_surface' not in st.session_state:
    st.session_state.content_surface = None
if 'total_content_height' not in st.session_state:
    st.session_state.total_content_height = 0
if 'is_first_input' not in st.session_state:
    st.session_state.is_first_input = True

st.title("Whiteboard Renderer")

# Display instruction based on whether it's the first input or a tweak
if st.session_state.is_first_input:
    instruction = "Enter problem description:"
else:
    instruction = "Enter tweak:"

# Input field for user input
user_input = st.text_input(instruction)
submit_button = st.button("Submit")

# Process input when the submit button is clicked
if submit_button and user_input.strip():
    user_input = user_input.strip()
    if st.session_state.is_first_input:
        # First input: problem description
        st.session_state.problem_description = user_input
        try:
            with st.spinner("Generating whiteboard..."):
                # Generate whiteboard syntax using GPT
                whiteboard_syntax = generator.generate_syntax(st.session_state.problem_description)
                st.session_state.whiteboard_syntax = whiteboard_syntax
                elements = parse_syntax(whiteboard_syntax)
                st.session_state.elements = elements
                st.session_state.is_first_input = False
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        # Subsequent inputs: tweaks
        tweak_description = user_input
        try:
            with st.spinner("Updating whiteboard..."):
                # Generate updated syntax using GPT
                whiteboard_syntax = generator.generate_tweak(
                    st.session_state.problem_description,
                    st.session_state.whiteboard_syntax,
                    tweak_description
                )
                st.session_state.whiteboard_syntax = whiteboard_syntax
                elements = parse_syntax(whiteboard_syntax)
                st.session_state.elements = elements
        except Exception as e:
            st.error(f"Error: {e}")

# Render the whiteboard content if elements are available
if st.session_state.elements:
    width = 1200  # Width of the content surface
    height = 5000  # Height of the content surface (adjust as needed)
    try:
        content_surface, total_content_height = render_whiteboard(
            st.session_state.elements, width, height
        )
        st.session_state.content_surface = content_surface
        st.session_state.total_content_height = total_content_height
    except Exception as e:
        st.error(f"Error rendering whiteboard: {e}")

# Display the rendered image in Streamlit
if st.session_state.content_surface:
    # Convert the Pygame surface to a PIL image
    image = surface_to_image(st.session_state.content_surface)
    # Crop the image to the total content height to remove empty space
    image = image.crop((0, 0, width, st.session_state.total_content_height))
    # Display the image in Streamlit
    st.image(image, use_column_width=True)

    # Optionally, save the image locally for testing purposes
    # image.save('whiteboard_output.png')

# Optional: Display the whiteboard syntax for debugging
with st.expander("Show Whiteboard Syntax"):
    st.code(st.session_state.whiteboard_syntax, language='plain')

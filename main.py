from render import parse_syntax, render_whiteboard
from gpt import GPTWhiteboardGenerator
import pygame
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

def main():
    # Initialize the GPTWhiteboardGenerator with the API key
    generator = GPTWhiteboardGenerator(API_KEY)

    # Prompt the user for a problem description
    problem_description = input("Enter a math problem to generate whiteboard syntax: ")

    try:
        # Generate whiteboard syntax using GPT
        print("Generating whiteboard syntax...")
        whiteboard_syntax = generator.generate_syntax(problem_description)
        print("Whiteboard syntax generated successfully.")
        print(whiteboard_syntax)

        # Parse the generated syntax into elements
        elements = parse_syntax(whiteboard_syntax)
        print("Parsed Elements:", elements)

        # Initialize the pygame rendering loop
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Whiteboard Renderer")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Render the whiteboard elements
            render_whiteboard(screen, elements)

            # Limit frame rate
            clock.tick(30)

        pygame.quit()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

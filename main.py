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

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((1600, 1000))
    pygame.display.set_caption("Whiteboard Renderer")
    clock = pygame.time.Clock()

    # Initialize variables
    problem_description = ""
    whiteboard_syntax = ""
    elements = []
    user_text = ""
    font = pygame.font.Font(None, 32)

    LEFT_MARGIN = 120  # Space for the input box
    input_box = pygame.Rect(20, 60, 280, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_active

    active = True  # Start with the input box active
    done = False
    loading = False

    scroll_offset = 0
    scroll_speed = 30  # Adjust as needed
    max_scroll = 0  # Initialize max_scroll

    # Placeholder for content surface and total content height
    content_surface = None
    total_content_height = 0

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset += event.y * scroll_speed
                # Limit scroll_offset to prevent scrolling too far
                max_scroll = total_content_height - screen.get_height()
                scroll_offset = max(-max_scroll, min(0, scroll_offset))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        user_input = user_text.strip()
                        user_text = ""
                        if not loading:
                            if problem_description == "":
                                # First input is the problem description
                                problem_description = user_input
                                try:
                                    loading = True
                                    # Update display to show loading
                                    screen.fill((255, 255, 255))
                                    instruction_text = font.render("Loading...", True, (0, 0, 0))
                                    screen.blit(instruction_text, (20, 20))
                                    pygame.display.flip()

                                    # Generate whiteboard syntax using GPT
                                    whiteboard_syntax = generator.generate_syntax(problem_description)
                                    elements = parse_syntax(whiteboard_syntax)
                                    loading = False

                                    # Render content surface
                                    content_surface, total_content_height = render_whiteboard(
                                        elements, screen.get_width(), 5000  # Adjust height as needed
                                    )
                                except Exception as e:
                                    print(f"Error: {e}")
                                    loading = False
                            else:
                                # Subsequent inputs are tweaks
                                tweak_description = user_input
                                try:
                                    loading = True
                                    # Update display to show loading
                                    screen.fill((255, 255, 255))
                                    instruction_text = font.render("Loading...", True, (0, 0, 0))
                                    screen.blit(instruction_text, (20, 20))
                                    pygame.display.flip()

                                    # Generate updated syntax using GPT
                                    whiteboard_syntax = generator.generate_tweak(
                                        problem_description, whiteboard_syntax, tweak_description
                                    )
                                    elements = parse_syntax(whiteboard_syntax)
                                    loading = False

                                    # Re-render content surface with updated elements
                                    content_surface, total_content_height = render_whiteboard(
                                        elements, screen.get_width(), 5000  # Adjust height as needed
                                    )
                                except Exception as e:
                                    print(f"Error: {e}")
                                    loading = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

        # Render the screen
        screen.fill((255, 255, 255))  # White background

        # Blit the content surface onto the screen with scroll offset
        if content_surface:
            # Limit scroll_offset to prevent scrolling too far
            max_scroll = max(0, total_content_height - screen.get_height())
            scroll_offset = max(-max_scroll, min(0, scroll_offset))

            # Blit the content surface onto the screen at the correct position
            screen.blit(content_surface, (LEFT_MARGIN, scroll_offset))

        # Render instructions and input box
        instruction = "Enter problem description:" if problem_description == "" else "Enter tweak:"
        instruction_surface = font.render(instruction, True, (0, 0, 0))
        screen.blit(instruction_surface, (20, 20))

        # Render the input box
        txt_surface = font.render(user_text, True, (0, 0, 0))
        width = max(280, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        # Display loading message if necessary
        if loading:
            loading_surface = font.render("Loading...", True, (255, 0, 0))
            screen.blit(loading_surface, (20, input_box.y + input_box.h + 10))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()

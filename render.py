import pygame
import re
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np


# Colors
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "grey": (128, 128, 128),
    "darkred": (139, 0, 0),
    "darkgreen": (0, 100, 0),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "darkblue": (0, 0, 139),
    "darkgrey": (105, 105, 105),
}

# Helper function for rendering LaTeX
def render_latex(content, size, color):
    """Render LaTeX content to a Pygame surface."""
    plt.rc('text', usetex=False)
    plt.rcParams['text.color'] = np.array(color) / 255  # Apply color
    fig, ax = plt.subplots(figsize=(size / 40, size / 40), dpi=100)
    ax.text(0.5, 0.5, content, fontsize=size, ha='center', va='center')
    ax.axis('off')

    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)

    # Convert to Pygame surface
    buf.seek(0)
    latex_image = pygame.image.load(buf, 'png')
    buf.close()

    return latex_image

# Parse Syntax
def parse_syntax(syntax):
    elements = []
    for line in syntax.strip().split("\n"):
        if line.startswith("#") or not line.strip():  # Ignore comments and empty lines
            continue
        if line.startswith("[group"):
            group_attributes = {"type": "group"}
            matches = re.findall(r'(\w+)=(".*?"|\(.*?\)|\S+)', line)
            for key, value in matches:
                if key == "at":
                    value = tuple(map(int, value.strip("()").split(",")))
                group_attributes[key] = value
            elements.append(group_attributes)
            continue
        if line.startswith("[end group"):
            elements.append({"type": "end group"})
            continue

        # Parse element type
        element_type_end = line.find(" ")
        element_type = line[1:element_type_end]
        attributes = {}

        # Parse attributes using regex
        attributes_string = line[element_type_end + 1:]
        matches = re.findall(r'(\w+)=(".*?"|\(.*?\)|\S+)', attributes_string)
        for key, value in matches:
            key = key.strip().lower()
            if value.startswith('"') and value.endswith('"'):
                value = value.strip('"')  # Handle quoted strings
            elif value.startswith("(") and value.endswith(")"):
                value = tuple(map(int, value.strip("()").split(",")))  # Handle tuples
            elif value.isdigit():
                value = int(value)  # Handle integers
            attributes[key] = value

        attributes["type"] = element_type
        elements.append(attributes)
    return elements

# Render Elements
def render_whiteboard(screen, elements):
    screen.fill(COLORS["white"])  # Clear the screen
    rendered_positions = []  # Track positions to avoid overlap
    current_group = []
    group_start_y = 0

    for element in elements:
        # Handle group elements
        if element["type"] == "group":
            current_group = []
            group_start_x, group_start_y = element.get("at", (50, len(rendered_positions) * 50))
            continue
        elif element["type"] == "end group":
            group_y = group_start_y
            for grouped_element in current_group:
                content = grouped_element["content"]
                color = COLORS.get(grouped_element.get("color", "black"), (0, 0, 0))
                size = grouped_element.get("size", 20)

                if "$" in content:
                    latex_surface = render_latex(content, size, color)
                    screen.blit(latex_surface, (group_start_x, group_y))
                    group_y += latex_surface.get_height() + 10
                else:
                    font = pygame.font.Font(None, size)
                    text_surface = font.render(content, True, color)
                    screen.blit(text_surface, (group_start_x, group_y))
                    group_y += text_surface.get_height() + 10
            continue

        if element.get("grouped", False):
            current_group.append(element)
            continue

        # Default position if `at` is not provided
        x, y = element.get("at", (50, len(rendered_positions) * 50))
        content = element.get("content", "")
        color = COLORS.get(element.get("color", "black"), (0, 0, 0))
        size = element.get("size", 20)

        # Check for horizontal overlap and adjust position
        if rendered_positions:
            last_x, last_y, last_height = rendered_positions[-1]
            if y < last_y + last_height:
                y = last_y + last_height + 10

        # Render element (LaTeX or text)
        if "$" in content:
            latex_surface = render_latex(content, size, color)
            screen.blit(latex_surface, (x, y))
            rendered_positions.append((x, y, latex_surface.get_height()))
        else:
            font = pygame.font.Font(None, size)
            text_surface = font.render(content, True, color)
            screen.blit(text_surface, (x, y))
            rendered_positions.append((x, y, text_surface.get_height()))

    pygame.display.flip()

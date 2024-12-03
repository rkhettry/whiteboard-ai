import pygame
import re
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Whiteboard with LaTeX Support")

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
    group_active = False
    for line in syntax.strip().split("\n"):
        if line.startswith("#") or not line.strip():  # Ignore comments and empty lines
            continue
        if line.startswith("[group"):
            group_active = True
            group_attributes = {"type": "group", "grouped": True}
            matches = re.findall(r'(\w+)=(".*?"|\(.*?\)|\S+)', line)
            for key, value in matches:
                if key == "at":
                    value = tuple(map(int, value.strip("()").split(",")))
                group_attributes[key] = value
            elements.append(group_attributes)
            continue
        if line.startswith("[end group"):
            group_active = False
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

        # Add parsed element
        attributes["type"] = element_type
        attributes["grouped"] = group_active  # Mark grouped status
        elements.append(attributes)
    return elements

# Render Elements
def render_whiteboard(elements):
    screen.fill(COLORS["white"])  # Clear the screen
    rendered_positions = []  # Track positions to avoid overlap
    current_group = []

    for element in elements:
        # Skip group elements that lack content
        if element["type"] in ["group", "end group"]:
            if element["type"] == "group":
                current_group = []
                group_start_x, group_start_y = element.get("at", (50, len(rendered_positions) * 50))
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

        # Render element (LaTeX or text)
        if "$" in content:
            latex_surface = render_latex(content, size, color)
            screen.blit(latex_surface, (x, y))
            rendered_positions.append((x, y + latex_surface.get_height()))
        else:
            font = pygame.font.Font(None, size)
            text_surface = font.render(content, True, color)
            screen.blit(text_surface, (x, y))
            rendered_positions.append((x, y + text_surface.get_height()))

    pygame.display.flip()

# Example Syntax for Whiteboard
WHITEBOARD_SYNTAX = """
[text id=1] content="Problem: Find the integral of $4x$" at=(50,50) color=darkred size=36
[math id=2] content="$\int 4x \, dx$" at=(50,120) color=blue size=32
[annotation id=3] content="Step 1: Use the power rule for integration: $\int x^n \, dx = \frac{x^{n+1}}{n+1} + C$" at=(50,200) color=darkgreen size=28    
[math id=4] content="$\int 4x \, dx = 4 \cdot \frac{x^{1+1}}{1+1} + C$" at=(50,260) color=purple size=32
[annotation id=5] content="Step 2: Simplify the expression" at=(50,320) color=darkgreen size=28
[math id=6] content="$= 2x^2 + C$" at=(50,380) color=purple size=32
[text id=7] content="Answer: The integral of $4x$ is $2x^2 + C$" at=(50,440) color=green size=34

[group id=8 at=(50,520)]
[text id=9] content="Extra Practice: Find the integral of $5x^2$" color=darkblue size=28
[annotation id=10] content="Hint: Use the power rule: $\int x^n \, dx = \frac{x^{n+1}}{n+1} + C$" color=darkgrey size=26
[end group]
Whiteboard syntax generated successfully.
[text id=1] content="Problem: Find the integral of $4x$" at=(50,50) color=darkred size=36
[math id=2] content="$\int 4x \, dx$" at=(50,120) color=blue size=32
[annotation id=3] content="Step 1: Use the power rule for integration: $\int x^n \, dx = \frac{x^{n+1}}{n+1} + C$" at=(50,200) color=darkgreen size=28    
[math id=4] content="$\int 4x \, dx = 4 \cdot \frac{x^{1+1}}{1+1} + C$" at=(50,260) color=purple size=32
[annotation id=5] content="Step 2: Simplify the expression" at=(50,320) color=darkgreen size=28
[math id=6] content="$= 2x^2 + C$" at=(50,380) color=purple size=32
[text id=7] content="Answer: The integral of $4x$ is $2x^2 + C$" at=(50,440) color=green size=34

[group id=8 at=(50,520)]
[text id=9] content="Extra Practice: Find the integral of $5x^2$" color=darkblue size=28
[annotation id=10] content="Hint: Use the power rule: $\int x^n \, dx = \frac{x^{n+1}}{n+1} + C$" color=darkgrey size=26
[end group]

"""




# Parse the example syntax
elements = parse_syntax(WHITEBOARD_SYNTAX)

# DEBUG: Print parsed elements
print("Parsed Elements:", elements)

# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    render_whiteboard(elements)

# Quit Pygame
pygame.quit()

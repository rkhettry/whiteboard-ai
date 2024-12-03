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
def render_latex(content, size, color, MAX_WIDTH):
    """Render LaTeX content to a Pygame surface."""
    plt.rc('text', usetex=True)
    plt.rcParams['text.color'] = np.array(color) / 255  # Apply color
    fig, ax = plt.subplots(figsize=(size / 20, size / 20), dpi=100)
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

# Function to render graphs
def render_graph(content, domain, size, color, surface, position):
    """Render a graph to the Pygame surface."""
    x = np.linspace(domain[0], domain[1], 1000)
    y = eval(content)

    plt.figure(figsize=(size / 100, size / 100))
    plt.plot(x, y, color=np.array(color) / 255)
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

    buf.seek(0)
    graph_image = pygame.image.load(buf, 'png')
    buf.close()

    surface.blit(graph_image, position)

# Parse Syntax
def parse_syntax(syntax):
    elements = []
    for line in syntax.strip().split("\n"):
        if line.startswith("#") or not line.strip():
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

# Function to render the whiteboard
def render_whiteboard(elements, width, height):
    """Render the whiteboard elements onto a Pygame surface."""
    content_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    content_surface.fill((255, 255, 255, 0))  # Transparent background

    MAX_WIDTH = width - 40
    y_position = 20  # Starting y position

    for element in elements:
        size = int(element.get("size", 20))
        content = element.get("content", "")
        color = COLORS.get(element.get("color", "black"), (0, 0, 0))
        at = element.get("at", (50, y_position))
        element_type = element.get("type")

        if element_type == "text":
            font = pygame.font.Font(None, size)
            text_surface = font.render(content, True, color)
            content_surface.blit(text_surface, at)
            y_position += size * 1.5
        elif element_type == "math":
            latex_surface = render_latex(content, size, color, MAX_WIDTH)
            content_surface.blit(latex_surface, at)
            y_position += latex_surface.get_height() + 10
        elif element_type == "graph":
            equation = element.get("equation", "x**2")
            domain = element.get("domain", (-10, 10))
            render_graph(equation, domain, size, color, content_surface, at)
            y_position += size + 10
        elif element_type == "table":
            headers = element.get("headers", [])
            rows = element.get("rows", [])
            # Render the table (to be implemented)
            pass
        elif element_type == "shape":
            # Render shapes like circles, rectangles, etc. (to be implemented)
            pass

    return content_surface

# Test the renderer with advanced syntax
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1600, 900))
    pygame.display.set_caption("Whiteboard Renderer Test")

    syntax = """
    [text id=1] content="Problem: Plot the graph of $y = x^2$" at=(50,50) color=darkred size=36
    [math id=2] content="$y = x^2$" at=(50,120) color=blue size=32
    [graph id=3] equation="x**2" domain=(-10,10) at=(50,200) color=green size=300
    [text id=4] content="Answer: The graph is displayed above." at=(50,520) color=darkgreen size=28
    """
    elements = parse_syntax(syntax)

    content_surface = render_whiteboard(elements, 1600, 900)
    screen.blit(content_surface, (0, 0))
    pygame.display.flip()

    # Wait for user to close the window
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)

class GPTWhiteboardGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_syntax(self, problem: str) -> str:
        """
        Send problem to the assistant and get Whiteboard Syntax back using function calling.
        """
        try:
            ai_prompt = """
Your task is to generate Whiteboard Syntax that accurately represents the following problem.
The syntax will be rendered on a virtual whiteboard, so your output must adhere to specific formatting rules to ensure a clean, visually appealing, and well-aligned presentation.

---

Whiteboard Syntax Overview:

Supported Elements:
- [text]: General text (e.g., problem descriptions, answers).
- [math]: Mathematical expressions written in LaTeX for proper rendering.
- [annotation]: Step-by-step annotations or explanations.
- [group]: A container to organize related content like extra practice or hints.

Attributes:
- id: A unique identifier for the element.
- content: The main content of the element. For math, use LaTeX enclosed in $...$.
- at: The position of the element, specified as a tuple (x, y).
- color: Choose a color for the element from the provided palette.
- size: The font size of the text or math.

---

Color Palette:
The following colors are available for use. Select complementary and visually pleasing combinations:
- red, green, blue, black, white, grey
- darkred, darkgreen, purple, orange, darkblue, darkgrey

---

Positioning Rules:
- Starting Position: The first element starts at (50, 50).
- Spacing: To avoid overlap, add vertical spacing based on the font size:
  spacing = size * 1.5
- Alignment:
  - Elements should align vertically unless grouped.
  - Horizontal positions should avoid overlap by adjusting the x coordinate as needed.
- Grouped Content: Place grouped elements at a distinct starting position (e.g., (50, 400)).

---

Structure:
1. Problem Description:
   - Begin with a [text] or [math] element describing the problem.
   - Use a large font size (e.g., size = 36).
   - Example: [text] content="Problem: Solve for the derivative of $x^3$"

2. Steps:
   - Use [annotation] to explain each step.
   - Use [math] to show equations or mathematical expressions.

3. Solution:
   - Conclude with a [text] or [math] element for the solution.
   - Highlight the answer using a visually distinct color (e.g., green or blue).

4. Hints or Extra Practice:
   - Group hints or additional problems in a [group] element for clarity.

---

Examples:

Example 1: Problem with Derivative
[text id=1] content="Problem: Solve for the derivative of $x^3$" at=(50,50) color=darkred size=36
[math id=2] content="$f(x) = x^3$" at=(50,120) color=blue size=32
[annotation id=3] content="Step 1: Recall the rule: $\\frac{{d}}{{dx}}[x^n] = nx^{{n-1}}$" at=(50,200) color=darkgreen size=28
[math id=4] content="$\\frac{{d}}{{dx}}[x^3] = 3x^2$" at=(50,260) color=purple size=32
[text id=5] content="Answer: The derivative of $x^3$ is $3x^2$" at=(50,340) color=green size=34

[group id=6 at=(50,420)]
[text id=7] content="Extra Practice: Find the derivative of $x^4$" color=darkblue size=28
[annotation id=8] content="Hint: Use the power rule: $\\frac{{d}}{{dx}}[x^n] = nx^{{n-1}}$" color=darkgrey size=26
[end group]

---

AI Task:
When provided with a problem description, generate Whiteboard Syntax following these rules:
- Ensure proper alignment (spacing vertically and horizontally).
- Select colors from the palette to create a visually appealing theme.
- Use appropriate font sizes for problem, steps, hints, and answers.
- Structure the syntax clearly, with no overlapping elements.
- Include optional hints or extra practice grouped at the bottom.

Please return **only** the Whiteboard Syntax without any additional text or formatting.
"""

            # Define the function that the model can call
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "generate_whiteboard_syntax",
                        "description": "Generates Whiteboard Syntax for a given problem.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "whiteboard_syntax": {
                                    "type": "string",
                                    "description": "The generated Whiteboard Syntax representing the solution to the problem.",
                                }
                            },
                            "required": ["whiteboard_syntax"],
                        }
                    }
                }
            ]

            # Prepare the messages
            messages = [
                {"role": "system", "content": ai_prompt},
                {"role": "user", "content": problem}
            ]

            # Make the API call using the client
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "generate_whiteboard_syntax"}},
                temperature=0.2,
            )

            # Extract the assistant's message
            message = response.choices[0].message

            # Check if the assistant called the function
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                try:
                    args = json.loads(function_args)
                except json.JSONDecodeError:
                    raise Exception(f"Invalid JSON in function arguments: {function_args}")
                syntax = args.get('whiteboard_syntax')
                if syntax:
                    return syntax
                else:
                    raise Exception("Function arguments did not contain 'whiteboard_syntax'")
            else:
                # Assistant didn't call the function, return the content
                return message.content or ""

        except Exception as e:
            raise Exception(f"Error generating solution: {str(e)}")

# Example usage
if __name__ == "__main__":
    generator = GPTWhiteboardGenerator(API_KEY)
    problem_description = "Solve the quadratic equation $x^2 - 5x + 6 = 0$"
    try:
        syntax = generator.generate_syntax(problem_description)
        print(syntax)
    except Exception as e:
        print(f"Error: {e}")
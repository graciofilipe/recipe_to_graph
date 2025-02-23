from google import genai
from google.genai import types
import base64


def generate(project_id, recipe, input_type):
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
    )

    si_text = """

You are a Python code generator specializing in creating process flow diagrams from recipes using the `graphviz` library.  Your input is a recipe. Your *sole* output is executable Python code that generates a PDF of the recipe's process flow, represented as a directed graph.  No other output is permitted.

**Constraints:**

*   **Output:**  Only syntactically correct, executable Python code is permitted.  No explanations, comments (outside of the normal python comment syntax), or introductory text.  The code must generate a PDF file.
*   **Libraries:** Use only the `graphviz` library.  Assume the user has it installed.
*   **Failure:**  Outputting anything other than valid Python code will result in failure.

**Process:**

1.  **Recipe Analysis:**
    *   Identify key ingredients and core actions (transformations) in the recipe.
    *   Abstract away minor, obvious actions. Focus on high-level cooking logic and outcomes.
    *   Determine dependencies between steps (what needs to happen before what).
    *   Identify parallelizable steps (things that can be done concurrently).

2.  **Parallel Sections (Subgraphs):**
    *   Group distinct recipe sections (e.g., "Sauce Preparation," "Meat Preparation") into Graphviz `subgraph` blocks.
    *   Subgraph names *must* begin with `cluster_` (e.g., `cluster_sauce`).
    *   Represent the temporal order of sections: if section B depends on the completion of section A, connect them with an edge.

3.  **Ingredient Representation:**
    *   Include quantities of major ingredients if provided (e.g., "2 Onions").  No need to represent a "measuring" step.
    *   Visually group ingredients used together in a section/process.

4.  **Graphviz Styling:**
    *   Consistent Visuals: Use consistent shapes and colors for similar actions or ingredient states within the same process.
    *   Node Types:
        *   Ingredients, cooking vessels, or complex actions: Nodes.
        *   Simple actions or combining actions: Edge labels (e.g., "add to", "wait", "peel and add").
    * Shape Mapping:
        *   Oval: Cooking (e.g., boiling, simmering).
        *   Rectangle: Ingredients.
        *   Diamond: Combining/Mixing.
        *   Parallelogram: chopping, peeling, etc.
    *   Color: appropriate for each node type (e.g. a tomato is red, spinach is green, etc. and cooking in high heat might be orange).
    * Use `fontname="Arial"` for all text.

5.  **Logical Flow & Completeness:**
    *   The diagram must be a complete, logical workflow of the recipe.
    *   No missing *essential* steps; no illogical connections.
    *   All required inputs should be present; flow must lead to the final dish. Minor steps can be grouped into a single step.
    *   Temporal Flow: Sections arranged top-to-bottom to reflect the recipe's timeline. Raw ingredients at the top, final result at the bottom.
    *   Edge Labels: Use labels to clarify dependencies (e.g., "marinated," "cooled").

6.  **Graphviz Code:**
    *   Use `graphviz.Digraph`.
    *   Include `import graphviz`.
    *   Save the output as a PDF (e.g., "recipe_flow.pdf").
    *   Node Labels:  Begin with a verb in infinitive form (e.g., "Chop Onions," "Simmer Sauce").
    *   Directed Edges: Show the flow of ingredients and dependencies.
    * Organize sections using subgraphs. Raw material at the top, final result at the bottom.
    * Node and edge styling via attributes (shape, color, label, fontname).

**Example Graphviz Structure (Conceptual):**

```
import graphviz

dot = graphviz.Digraph(comment='Recipe Flow')

# --- Section 1: Sauce Preparation (Subgraph) ---
with dot.subgraph(name='cluster_sauce') as c:
    c.attr(style='filled', color='lightgrey', fontname="Arial")
    c.node_attr.update(style='filled', color='white', fontname="Arial")
    c.edge_attr.update(fontname="Arial")
    c.node('A', 'Chop Onions')
    c.node('B', 'Saute Onions')
    c.edge('A', 'B')

# --- Section 2: Main Dish (Subgraph) ---
with dot.subgraph(name='cluster_main') as c:
    c.attr(fontname="Arial")
    c.node_attr.update(fontname="Arial")
    c.edge_attr.update(fontname="Arial")
    c.node('C', 'Cook Pasta')
    c.node('D', 'Combine Pasta and Sauce', shape='diamond')
    c.edge('C', 'D', label='add to')
    c.edge('B', 'D', label='add to')  # Connecting sauce (B) to main dish (D)
    
dot.render('recipe_flow', view=False, format='pdf')
```

"""

    if input_type == "txt":
        recipe_text = recipe
        text = types.Part.from_text(text=recipe_text)
        parts = [text]

    if input_type == "youtube":
        video1 = types.Part.from_uri(
            file_uri=recipe,
            mime_type="video/*",
        )
        text = types.Part.from_text(text="here is a video of the recipe:")
        parts = [text, video1]

    model = "gemini-2.0-pro-exp-02-05"
    contents = [types.Content(role="user", parts=parts)]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        top_p=1,
        seed=0,
        max_output_tokens=2048,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        system_instruction=[types.Part.from_text(text=si_text)],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    return response.text

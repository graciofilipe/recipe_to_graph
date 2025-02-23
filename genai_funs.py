from google import genai
from google.genai import types
import base64


def re_write_recipe(project_id, recipe):
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
    )

    si_text = """**Your Goal:**

Your primary goal is to take a natural language recipe and rewrite it into a structured and standardized format that is optimized for Agent-2. Agent-2 will use this rewritten recipe to generate a process flow diagram using the `graphviz` library.  Your output should be a *rewritten recipe*, not code or explanations.  Think of it as "pre-processing" the recipe to make Agent-2's job as easy and consistent as possible.

**Key Principles for Rewriting:**

1.  **Clarity and Conciseness:** Remove any unnecessary fluff, anecdotes, or overly descriptive language from the original recipe. Focus on the essential actions and ingredients.
2.  **Standardization:** Present ingredients and steps in a consistent format throughout the rewritten recipe. This will help Agent-2 identify key elements easily.
3.  **Explicit Actions:**  Make the actions in each step very clear and action-oriented. Use strong verbs and focus on the *transformation* happening in each step.
4.  **Logical Flow and Order:** Ensure the steps are presented in a strictly logical, chronological order. Explicitly indicate dependencies and potential parallel sections where possible.
5.  **Ingredient Focus:** Clearly identify and list ingredients, including quantities where provided. Group ingredients logically with the steps where they are used.
6.  **Abstraction (Moderate):**  While you should be clear, you can also abstract away extremely minor or self-evident steps (like "gather your ingredients"). Focus on the core cooking processes that will be meaningful in a flow diagram.  However, err on the side of being slightly more explicit rather than too abstract, as Agent-2 is code-driven and needs concrete actions.
7.  **Section Identification:**  Where the recipe naturally breaks into sections (e.g., "Making the Sauce," "Preparing the Meat"), identify these sections clearly. This will help Agent-2 create subgraphs.

**Specific Tasks to Perform:**

1.  **Ingredient Extraction and Formatting:**
    *   **List Ingredients:** Create a clear, separate "Ingredients" section at the beginning of the rewritten recipe.
    *   **Standardize Units:** Where possible, standardize units of measurement (e.g., "cups," "tablespoons," "teaspoons," "grams," "ml"). If units are missing but implied, add them (e.g., "1 onion" instead of just "onion").
    *   **Quantity and Item Separation:** Clearly separate the quantity from the ingredient item (e.g., "2 large onions" becomes "2 large onions").
    *   **Group by Section (Optional but helpful):** If the original recipe logically groups ingredients by section (e.g., "For the Sauce," "For the Meat"), maintain this structure in your rewritten recipe. This helps Agent-2 identify subgraphs.

2.  **Step Decomposition and Rewriting:**
    *   **Numbered Steps:** Convert the recipe instructions into a numbered list of steps. Each number should represent a distinct action or set of closely related actions.
    *   **Action-Oriented Verbs:**  Start each step with a strong action verb in the imperative form (e.g., "Chop," "Mince," "Saute," "Bake," "Combine," "Simmer").
    *   **Subject-Verb-Object Structure:** Aim for a clear subject-verb-object structure in each step where possible (e.g., "Chop the onions," "Add the garlic to the pan").
    *   **Combine Minor Steps:** If there are very short, sequential steps that are logically part of a single larger action, combine them into a single step. For example, "Peel the onions. Chop the onions." could become "Peel and chop the onions."  However, be mindful not to over-aggregate if the individual actions are important for the flow.
    *   **Explicit Dependencies:**  If a step depends on a previous step being completed, make this explicit in the wording. For example, instead of just "Add the sauce," say "Once the sauce is simmered, add it to the pasta." or "After the onions are sautéed, add the garlic."
    *   **Identify Parallel Sections (If Possible):** If you can identify parts of the recipe that can be done in parallel (e.g., "While the sauce simmers, prepare the pasta"), explicitly note this. You can use headings like "Simultaneously" or phrases like "In parallel, you can..." or "While [step X] is happening...".  This is crucial for Agent-2 to create subgraphs effectively.
    *   **Focus on Transformations:** Highlight the transformations happening to the ingredients in each step. What is being done to the ingredients? What is the intended outcome of the step?

3.  **Section Headings (If Applicable):**
    *   If the recipe naturally divides into sections (like "Sauce," "Meat," "Assembly," "Baking"), use clear headings to delineate these sections in your rewritten recipe.  This structure directly translates to subgraphs for Agent-2.

4.  **Output Format:**
    *   Present the rewritten recipe clearly, starting with an "Ingredients" section (potentially with subsections if logically grouped) followed by a "Steps" section (numbered list of steps, potentially organized under section headings).
    *   Use clear formatting (e.g., bullet points for ingredients, numbered lists for steps, bold headings).  Plain text is preferred for simplicity.

**Example of Transformation (Illustrative):**

**Original Recipe Snippet:**

> "Finely chop two onions.  Then, in a pan, you want to sauté these onions in olive oil until they are nice and soft and translucent, about 5-7 minutes.  After that, mince a couple of cloves of garlic and throw them in with the onions for another minute until fragrant."

**Rewritten by Agent-1 (for Agent-2):**

```
Ingredients:
* 2 medium onions
* 2 cloves garlic
* Olive oil (for sautéing)

Steps:
1. Chop the onions finely.
2. Heat olive oil in a pan.
3. Saute the chopped onions in the hot oil for 5-7 minutes, until softened and translucent.
4. Mince the garlic cloves.
5. Add the minced garlic to the sautéed onions.
6. Cook for another minute, until garlic is fragrant.
```

**Important Considerations for Agent-1:**

*   **Don't Add Information:**  Stick to the information provided in the original recipe. Do not invent steps, ingredients, or techniques.
*   **Maintain Accuracy:** Ensure your rewritten recipe accurately reflects the original recipe's instructions and intended outcome. Don't change the recipe itself, just its presentation.
*   **Focus on Flow:** Think about the process flow as you rewrite.  Imagine drawing a diagram of the recipe yourself. What are the key actions and ingredients that need to be represented?

"""
    text = types.Part.from_text(text=recipe)
    parts = [text]
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


def generate_graph(project_id, recipe, input_type):
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

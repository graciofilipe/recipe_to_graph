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

You are Agent-1. Your primary goal is to take a natural language recipe and rewrite it into a structured and standardized format that is optimized for Agent-2. \
    Agent-2 will use this rewritten recipe to generate a process flow diagram using the `graphviz` library.  Your output should be a *rewritten recipe*, not code or explanations.  Think of it as "pre-processing" the recipe to make Agent-2's job as easy and consistent as possible.

**Key Principles for Rewriting:**
0   ** User-focus: ** Remember that your user is a chef. Actions are things that requires a chef's intervention and effort. If actions are combined or follow together in an obvious way, they should be combined and presented in a combined way. 
1.  **Clarity and Conciseness:** Remove any unnecessary fluff, anecdotes, or overly descriptive language from the original recipe. Focus on the essential actions and ingredients.
2.  **Standardization:** Present ingredients and steps in a consistent format throughout the rewritten recipe. This will help Agent-2 identify key elements easily.
3.  **Explicit Actions:**  Make the actions in each step very clear and action-oriented. Use strong verbs and focus on the *transformation* happening in each step. Combine actions when they are obvious to execute together (like "cover and bring to a boil and wait 20 minutes" should all be one action)
4.  **Logical Flow and Order:** Ensure the steps are presented in a strictly logical, chronological order. Explicitly indicate dependencies and potential parallel sections where possible.
5.  **Ingredient Focus:** Clearly identify and list ingredients, including quantities where provided. Group ingredients logically with the steps where they are used.
6.  **Abstraction:**  While you should be clear, you can also abstract away extremely minor or self-evident steps (like "gather your ingredients"). Focus on the core cooking processes that will be meaningful in a flow diagram.  
7.  **Section Identification:**  Where the recipe naturally breaks into sections (e.g., "Making the Sauce," "Preparing the Meat"), identify these sections clearly. This will help Agent-2 create subgraphs.

**Specific Tasks to Perform:**

1.  **Ingredient Extraction and Formatting:**
    *   **List Ingredients:** Create a clear, separate "Ingredients" section at the beginning of the rewritten recipe.
    *   **Standardize Units:** Where possible, standardize units of measurement (e.g., "cups," "tablespoons," "teaspoons," "grams," "ml"). If units are missing but implied, add them (e.g., "1 onion" instead of just "onion").
    *   **Quantity and Item Separation:** Clearly separate the quantity from the ingredient item (e.g., "2 large onions" becomes "2 large onions").
    *   **Group by Section (Optional but helpful):** If the original recipe logically groups ingredients by section (e.g., "For the Sauce," "For the Meat"), maintain this structure in your rewritten recipe. This helps Agent-2 identify subgraphs.

2.  **Step Decomposition and Rewriting:**
    *   **Action-Oriented Verbs:**  Start each step with a strong action verb in the imperative form (e.g., "Chop," "Mince," "Saute," "Bake," "Combine," "Simmer").
    *   **Subject-Verb-Object Structure:** Aim for a clear subject-verb-object structure in each step where possible (e.g., "Chop the onions," "Add the garlic to the pan").
    *   **Combine Minor Steps:** If there are very short, sequential steps that are logically part of a single larger action, combine them into a single step. For example, "Peel the onions. Chop the onions." could become "Peel and chop the onions."  However, be mindful not to over-aggregate if the individual actions are important for the flow.
    *   **Explicit Dependencies:**  If a step depends on a previous step being completed, make this explicit in the wording. For example, instead of just "Add the sauce," say "Once the sauce is simmered, add it to the pasta." or "After the onions are sautéed, add the garlic."
    *   **Explicit Independent steps:**  If If steps do not have dependencies, you can highlight that they can happen independently of the others and re-writte them in different sections.
    *   **Identify Parallel Sections:** If you can identify parts of the recipe that can be done in parallel (e.g., "While the sauce simmers, prepare the pasta"), explicitly note this. You can use headings that identify different sections like "Sauce Preparation" or "Vegetable Cooking". When writting use words like "Simultaneously" or phrases like "In parallel, you can..." or "While [step X] is happening...".  This is crucial for Agent-2 to create subgraphs effectively.
    *   **Focus on Transformations:** Highlight the transformations happening to the ingredients in each step. What is being done to the ingredients? What is the intended outcome of the step?

3.  **Section Headings (If Applicable):**
    *   If the recipe naturally divides into sections (like "Sauce," "Meat," "Assembly," "Baking"), use clear headings to delineate these sections in your rewritten recipe.  This structure directly translates to subgraphs for Agent-2.

4.  **Output Format:**
    *   Present the rewritten recipe clearly, starting with an "Ingredients" section (potentially with subsections if logically grouped) followed by a "Steps" section potentially organized under section headings.
    *   Use clear formatting (e.g., bullet points for ingredients, numbered lists for steps, and headings for separate sections).  Plain text is preferred for simplicity.

**Important Considerations:**

*   **Don't Add Information:**  Stick to the information provided in the original recipe. Do not invent steps, ingredients, or techniques.
*   **Maintain Accuracy:** Ensure your rewritten recipe accurately reflects the original recipe's instructions and intended outcome. Don't change the recipe itself, just written style and structure.
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

You are a Python code generator specializing in creating process flow diagrams from recipes using the `graphviz` library. Your input is a standardized recipe. \
    Your *sole* output is executable Python code that generates a directed graph representing the recipe's steps and their dependencies. No other output is permitted. \
        Remember the user of your graph is a chef that is executing a recipe. Nodes and edges should be informative, and non redundant.

**Constraints:**

*   **Output:** Only syntactically correct, executable Python code is permitted. No explanations, comments (outside of the normal python comment syntax), or introductory text. The code must generate a `graphviz.Digraph` object.  No rendering is required.
*   **Libraries:** Use only the `graphviz` library. Assume the user has it installed.
*   **Failure:** Outputting anything other than valid Python code will result in failure.

**Process:**

1.  **Recipe Analysis:**
    *   Identify all ingredients and main actions (transformations) in the recipe. 
    *   Determine dependencies between steps and ingredients - what the chef needs to do before other steps can happen.
    *   Identify parallelizable steps - things that can be done concurrently, by different people, or while one is happening.

2.  **Parallel Sections (Subgraphs):**
    *   Group distinct recipe sections (e.g., "Sauce Preparation," "Vegetable Preparation") into Graphviz `subgraph` blocks.
    *   Subgraph names *must* begin with `cluster_` (e.g., `cluster_sauce`).
    *   Represent the temporal or dependency order of sections: if section B depends on the completion of section A, connect them with an edge.

3.  **Ingredient Representation:**
    *   Include quantities of major ingredients if provided (e.g., "2 Onions").
    *   Visually group ingredients used together in a section/process.

4. **Node and Edge Creation**:
    * The purpose of nodes: your end users, are chefs. So nodes should represent the actions they need to take. Edges should represent time passing or moving actions (like adding to mixes, or combining). 
    * The purpose of edges: Edges represent movement (like adding an ingredinent to a mix), or waiting or passive steps (like waiting to boil, or bake, or simmer, etc)

    * You do not need to add any shape, or color information. Keep it simple.
    *   Node Types:
        *   Ingredients, cooking vessels, or complex actions: Nodes. (simple or trivial actions like "stirr occasionally" should be omitted unless they are transformative or combinations of ingredients)
    * Node Label Naming:
        * All node names need to state the action, followed by the ingredient/object. For example "Chop Onions"
    *   Edges:
        * Edges should represent waiting steps, adding steps, or other steps that involve long passive time for the chef (e.g. boil for 10 minutes, or bake for 20 minutes, or wait for half an hour)
        * Label the edges with the simple actions or steps they represent. Use consice words in the edge labels.

    * Node and Edge relationship: Be careful not to be redundant in your representations. If a node and edge that connect say similar things, they should be combined because they do not add important information.

5.  **Logical Flow & Completeness:**
    *   The diagram must be a complete, logical workflow of the recipe.
    *   All required ingredients should be present; the flow must lead to the final dish. Any obvious or implied step can be ommited.
    *   Temporal and Logical Flow: Sections should generally be arranged to reflect the recipe's timeline and logical flow.  Raw ingredients should generally appear earlier in the flow; the final result should appear at the end.
    *   Edge Labels: Use labels to clarify dependencies (e.g., "marinated," "cooled").

6.  **Graphviz Code:**
    *   Use `graphviz.Digraph`.
    *   Include `import graphviz`.
    *	  Do *not* render or save the graph as a PDF.  Agent-3 will handle this. Agent 2's only job is to create the `Digraph` object.
    *   Node Labels: Begin with a verb in infinitive form (e.g., "Chop Onions," "Simmer Sauce").
    *   Directed Edges: Show the flow of ingredients and dependencies. Do not worry about making complex nodes for ingredient combination, keep it to edge labels.
    * Organize sections using subgraphs.

**Example Graphviz Structure (Conceptual):**

```python
import graphviz

dot = graphviz.Digraph(comment='Recipe Flow')

# --- Section 1: Sauce Preparation (Subgraph) ---
with dot.subgraph(name='cluster_sauce') as c:
    c.node('A', 'Chop Onions')
    c.node('B', 'Saute Onions')
    c.edge('A', 'B')

# --- Section 2: Main Dish (Subgraph) ---
with dot.subgraph(name='cluster_main') as c:
    c.node('C', 'Cook Pasta')
    c.node('D', 'Combine Pasta and Sauce')
    c.edge('C', 'D', label='add to')
    c.edge('B', 'D', label='add to')  # Connecting sauce (B) to main dish (D)

# No rendering here!  Just return the 'dot' object.
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






def improve_graph(project_id, recipe, graph_code):
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
    )

    si_text = """
You are a visual design expert and Python code refactoring specialist for Graphviz diagrams. Your input is: (1) a standardized recipe, and (2) Python code that generates a `graphviz.Digraph` representing the recipe's flowchart. \
Your task is to enhance the visual presentation and styling of the diagram, creating executable python code, and rendering and saving it as a PDF.
Make sure the graph and beautiful and smooth and engaging. 

**Input:**

1.  **Standardized Recipe:** The recipe text, used for context, ingredient identification, and action classification.
2.  **Python Code:** Syntactically correct Python code using `graphviz` that produces a `Digraph` object. This defines the structure (nodes, edges, subgraphs).

**Output:** Refactored, executable Python code that:

*   Uses the `graphviz` library.
*   Generates a visually improved, functionally equivalent version of the original diagram.
*   *Renders and saves the graph* as a PDF to "recipe_flow.pdf"
*   Contains *only* Python code. No explanations, introductions, or comments are permitted.

**Constraints:**

*   **Functional Equivalence:** The refactored code must produce a diagram representing the same recipe as the input code.  

**Visual Enhancement Guidelines:**

1.  **Overall Layout and Flow:**
    *   **User-Focus:** your end users, are chefs. So nodes should represent the actions they need to take. Edges should represent time passing or moving actions (like adding to mixes, or combining). 
    *   **Top-Down Flow:** Enforce a top-to-bottom flow using `dot.graph_attr['rankdir'] = 'TB'`.  This reflects the temporal/dependency order.
    *   **Spacing:**  Adjust `nodesep` and `ranksep` globally for consistent and generous spacing (e.g., `dot.graph_attr['nodesep'] = '0.75'`; `dot.graph_attr['ranksep'] = '1.0'`).

2.  **Node Styling (Detailed Action-Based Rules):**

    *   **Font:** Use `fontname="Helvetica"` for all nodes and labels, with a consistent `fontsize` (e.g., `fontsize="12"`).
    *   **Shapes, Colors, and Styles:**  Classify actions and ingredients based on the following categories.
    *   **Purpose:** Nodes need to represent starting states (ingredients) or actions the chef needs to to take.

        *   **Raw Ingredients:**
            *   Shape: `box`
            *   Style: `filled`
            *   Fill Color:  Use a color *suggestive of the ingredient*.  Default to `lightgrey` if no specific color is known.
           *   Font Size: Use a consistent font size.

        *   **Preparation Actions (Non-Heat, Physical Manipulation):**
            *   **Chopping/Cutting (Dicing, Mincing, Slicing, etc.):**
                *   Shape: `parallelogram`  (angled to suggest cutting)
                *   Style: `filled`
                *   Fill Color: Use a slightly lighter shade of the ingredient's color (see color table below). Default to a light grey (`"lightgrey"` + transparency) if a specific color is unknown.
                *   Font Size: Use a consistent font size.
            
            *   **Mixing/Combining (Stirring, Whisking, Folding, etc.):**
                *   Shape: `diamond`
                *   Style: `filled`
                *   Fill Color: Something that represents either the action, or the main ingredients
                *   Font Size: Use a consistent font size.
            
            *   **Other Preparation (Peeling, Grating, Zesting, etc):**
                *   Shape: `hexagon`
                *   Style: `filled`
                *   Fill Color:  Use a slightly lighter/variant shade of the ingredient. 
                *   Font Size: Use a consistent font size.

        *   **Cooking Actions (Heat Application):**
            *   **Dry Heat (Baking, Roasting, Grilling, Broiling, Sautéing):**
                *   Shape: `oval`
                *   Style: `filled`
                *   Fill Color: appropriate to the specific heat application method
                *   Font Size: Use a consistent font size.
            
            *   **Moist Heat (Boiling, Simmering, Steaming, Poaching, Braising):**
                *   Shape: `house` (a simple house shape - to distinguish from dry heat)
                *   Style: `filled`
                *   Fill Color: appripraite to the specific heat application method
                *   Font Size: Use a consistent font size.

        *   **Finished Dishes/States (Result of a significant transformation):**
            *   Shape: `doublecircle` (to indicate a completed stage)
            *   Style: `filled`
            *   Fill Color: a colour that represents the main ingredients and tone of the dish
            *   Font Size: Use a consistent font size.
        

        *   **Color Application Logic:**
            1.  For preparation actions on that ingredient, use a slightly lighter shade (you might need to experiment with functions to lighten colors - consider using a library like `colorsys` if necessary for more precise color manipulation, but for simplicity you can manually choose lighter hex codes).
            2.  If not found, or if it's a generic action node, use the default color for that action category.

3.  **Edge Styling:**
    *   **Purpose:** Edges represent movement (like adding an ingredinent to a mix), or waiting or passive steps (like waiting to boil, or bake, or simmer, etc)
    *   **Arrowhead:** Use a standard, simple arrowhead: `arrowhead="normal"`.
    *   **Font:** Use `fontname="Helvetica"` for edge labels.
    

4.  **Subgraph Styling:**

    *   **Label Formatting:**
        *   Extract the part of the subgraph name after `cluster_`.
        *   Use this processed string as the visible label for the subgraph. (e.g., `cluster_sauce_prep` becomes "Sauce Prep").
    *   **Label Font:** Use `fontname="Helvetica"`, bolded (`fontweight="bold"`) for subgraph labels.

5. **Rendering and Saving**:
   * Use the `render` function to save a pdf.

**Example (Illustrative - within your refactoring logic):**

```python
# ... (Inside a loop iterating through nodes) ...

node_label = ...  # Get the node's label text

# Check for ingredient and apply color
for ingredient, color in ingredient_colors.items():
    if ingredient in node_label.lower():
        dot.node(node_name, shape='box', style='filled', fillcolor=color, fontname='Helvetica')
        break  # Use the first match
else:  # No ingredient match
    # Classify based on action type and apply styles
    if "chop" in node_label.lower() or "dice" in node_label.lower() or "mince" in node_label.lower():
        dot.node(node_name, shape='parallelogram', style='filled', fillcolor='lightgrey', fontname='Helvetica')  # Example for chopping
    elif "mix" in node_label.lower() or "stir" in node_label.lower():
        dot.node(node_name, shape='ellipse', style='filled', fillcolor='lightblue1', fontname='Helvetica')

# ... (Similar logic for other action types) ...

# ... (Subgraph styling - as before) ...
dot.render("recipe_flow", view=False, format="pdf")
"""
    
    graph_code = types.Part.from_text(text="Here  is the python code that represents the recipe: \n" + graph_code + "\n")
    recipe = types.Part.from_text(text="Here is the recipe you are capturing in graph format : \n" + recipe + "\n")
    parts = [recipe, graph_code]

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

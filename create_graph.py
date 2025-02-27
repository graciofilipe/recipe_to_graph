import graphviz

dot = graphviz.Digraph(comment='Divorciados Recipe')
dot.graph_attr['layout'] = 'dot'
dot.graph_attr['rankdir'] = 'TB'
dot.graph_attr['nodesep'] = '0.7'
dot.graph_attr['ranksep'] = '1.0'

# --- Vegetable Cooking Subgraph ---
with dot.subgraph(name='cluster_vegetable_cooking') as c:
    c.attr(label='Vegetable Cooking', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    c.node('vegetables', 'Tomatillos, Tomatoes, Onion, Jalapenos, Garlic', shape='ellipse', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    c.node('boil_veg', 'Boil Vegetables', shape='house', style="rounded, filled", fillcolor="skyblue", fontname="Helvetica", fontsize="12")
    c.node('simmer_veg', 'Simmer (5 min)', shape='component', style="rounded, filled", fillcolor="lightgray", fontname="Helvetica", fontsize="12")
    c.edge('vegetables', 'boil_veg', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='add to pot')
    c.edge('boil_veg', 'simmer_veg', style='dashed', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='until covered', color='skyblue')
    c.node('drain_veg', 'Drain Vegetables', shape='ellipse', style="rounded, filled", fillcolor="powderblue", fontname="Helvetica", fontsize="12")
    c.edge('simmer_veg', 'drain_veg', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# --- Red Salsa Subgraph ---
with dot.subgraph(name='cluster_red_salsa') as c:
    c.attr(label='Red Salsa Preparation', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    c.node('red_ingredients', 'Cooked: Roma Tomatoes, 1/2 Onion, 1 Jalapeno, 1 Garlic Clove', shape='ellipse', style="rounded, filled", fillcolor="lightcoral", fontname="Helvetica", fontsize="12")
    c.node('salt1', '1/2 tsp Salt', shape='plaintext', style="", fontname="Helvetica", fontsize="12")
    c.node('blend_red', 'Blend Until Smooth', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    c.edge('drain_veg', 'red_ingredients', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label = 'take')
    c.edge('red_ingredients', 'blend_red', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('salt1', 'blend_red', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.node('fry_red_salsa', 'Fry Red Salsa', shape='oval', style="rounded, filled", fillcolor="tomato", fontname="Helvetica", fontsize="12")
    c.node('olive_oil1', '1 tsp Olive Oil', shape='plaintext', style="", fontname="Helvetica", fontsize="12")
    c.edge('olive_oil1', 'fry_red_salsa', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('blend_red', 'fry_red_salsa', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='1 min')
    c.node('red_salsa_bowl','Red Salsa Bowl', shape='doublecircle', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    c.edge('fry_red_salsa','red_salsa_bowl', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='transfer to')

# --- Green Salsa Subgraph ---
with dot.subgraph(name='cluster_green_salsa') as c:
    c.attr(label='Green Salsa Preparation', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    c.node('green_ingredients', 'Cooked: Tomatillos, 1/2 Onion, 1 Jalapeno, 1 Garlic Clove, Cilantro', shape='ellipse', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    c.node('salt2', '1/2 tsp Salt', shape='plaintext', style="", fontname="Helvetica", fontsize="12")
    c.node('blend_green', 'Blend Until Smooth', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    c.edge('drain_veg', 'green_ingredients', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label = 'take')
    c.edge('green_ingredients', 'blend_green', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('salt2', 'blend_green', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.node('fry_green_salsa', 'Fry Green Salsa', shape='oval', style="rounded, filled", fillcolor="tomato", fontname="Helvetica", fontsize="12")
    c.node('olive_oil2', '1 tsp Olive Oil', shape='plaintext', style="", fontname="Helvetica", fontsize="12")
    c.edge('olive_oil2', 'fry_green_salsa', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('blend_green', 'fry_green_salsa', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='1 min')
    c.node('green_salsa_bowl', 'Green Salsa Bowl', shape='doublecircle', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    c.edge('fry_green_salsa', 'green_salsa_bowl', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='transfer to')

# --- Egg Preparation Subgraph ---
with dot.subgraph(name='cluster_egg_prep') as c:
    c.attr(label='Egg Preparation', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    c.node('eggs', '4 Large Eggs', shape='ellipse', style="rounded, filled", fillcolor="lightyellow", fontname="Helvetica", fontsize="12")
    c.node('fry_eggs', 'Fry Eggs', shape='oval', style="rounded, filled", fillcolor="tomato", fontname="Helvetica", fontsize="12")
    c.node('olive_oil3', '1 tbsp Olive Oil', shape='plaintext', style="", fontname="Helvetica", fontsize="12")
    c.edge('olive_oil3', 'fry_eggs', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('eggs', 'fry_eggs', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='3 min')

# --- Final Assembly Subgraph ---
with dot.subgraph(name='cluster_final_assembly') as c:
    c.attr(label='Final Assembly', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    c.node('plate_eggs', 'Plate 2 Fried Eggs', shape='parallelogram', style="rounded, filled", fillcolor="lightblue", fontname="Helvetica", fontsize="12")
    c.edge('fry_eggs', 'plate_eggs', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.node('add_salsas', 'Add Red and Green Salsa', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    c.edge('plate_eggs', 'add_salsas', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('red_salsa_bowl', 'add_salsas', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='spoon')
    c.edge('green_salsa_bowl', 'add_salsas', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", label='spoon')
    c.node('garnish', 'Garnish', shape='parallelogram', style="rounded, filled", fillcolor="lightblue", fontname="Helvetica", fontsize="12")
    c.edge('add_salsas', 'garnish', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.node('cheese', 'Cotija Cheese', shape='plaintext', style="", fontname="Helvetica", fontsize="12")
    c.node('cilantro', 'Cilantro', shape='plaintext', style="", fontname="Helvetica", fontsize="12")
    c.edge('cheese', 'garnish', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('cilantro', 'garnish', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

    c.node('serve', 'Serve', shape='doublecircle', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    c.edge('garnish','serve', style='solid', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

dot.render("recipe_flow", view=False, format="pdf")
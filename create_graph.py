import graphviz

dot = graphviz.Digraph(comment='Lentil Soup Recipe')
dot.graph_attr['layout'] = 'dot'
dot.graph_attr['rankdir'] = 'TB'
dot.graph_attr['nodesep'] = '0.7'
dot.graph_attr['ranksep'] = '1.0'

# --- Helper Functions ---
def ingredient_color(ingredient):
    if "Onion" in ingredient:
        return "wheat"
    elif "Celery" in ingredient:
        return "palegreen"
    elif "Garlic" in ingredient:
        return "lightyellow"
    elif "Lentils" in ingredient:
        return "burlywood"
    elif "Chickpeas" in ingredient:
        return "cornsilk"
    elif "Rice" in ingredient:
        return "wheat"
    elif "Olive Oil" in ingredient:
        return "lemonchiffon"
    elif "Tomato Paste" in ingredient:
        return "tomato"
    elif "Ginger" in ingredient:
        return "lightgoldenrod1"
    elif "Turmeric" in ingredient:
        return "yellow"
    elif "Cinnamon" in ingredient:
        return "rosybrown"
    elif "Black Pepper" in ingredient:
        return "black"
    elif "Cayenne" in ingredient:
        return "orangered"
    elif "Diced Tomatoes" in ingredient:
        return "tomato"
    elif "Broth" in ingredient:
        return "skyblue"
    elif "Cilantro" in ingredient:
        return "forestgreen"
    elif "Parsley" in ingredient:
        return "limegreen"
    elif "Lemon" in ingredient:
        return "yellow"
    return "lightgray"

def action_color(action, ingredient=None):
    if "Chop" in action or "Mince" in action:
        return "lightblue" if ingredient is None else ingredient_color(ingredient).replace("1", "2").replace("3", "4")
    elif "Drain" in action or "Rinse" in action:
        return "powderblue"
    elif "Saute" in action or "Cook" in action:
        return "coral"
    elif "Add" in action and "Spices" in action:
        return "lightsalmon"
    elif "Simmer" in action:
        return "skyblue"
    elif "Heat" in action:
        return "coral"
    return "lightgray"

# --- Prepare Vegetables Subgraph ---
with dot.subgraph(name='cluster_prepare_vegetables') as veg_prep:
    veg_prep.attr(label='Prepare Vegetables', fontname="Helvetica", fontsize="14", fontweight="bold", style="dashed", pencolor="gray")
    veg_prep.node('Chop Onion and Celery', 'Chop Onion and Celery', shape='parallelogram', style="rounded, filled", fillcolor=action_color("Chop", "Onion"), fontname="Helvetica", fontsize="12")
    veg_prep.node('Mince Garlic', 'Mince Garlic', shape='parallelogram', style="rounded, filled", fillcolor=action_color("Mince", "Garlic"), fontname="Helvetica", fontsize="12")
    veg_prep.node('Onion', '1 Medium Onion,\nfinely chopped', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Onion"), fontname="Helvetica", fontsize="12")
    veg_prep.node('Celery', '1 Stalk Celery,\nfinely chopped', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Celery"), fontname="Helvetica", fontsize="12")
    veg_prep.node('Garlic', '2 Cloves Garlic,\nminced', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Garlic"), fontname="Helvetica", fontsize="12")

    veg_prep.edge('Onion', 'Chop Onion and Celery', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    veg_prep.edge('Celery', 'Chop Onion and Celery', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    veg_prep.edge('Garlic', 'Mince Garlic', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# --- Prepare Legumes and Rice Subgraph ---
with dot.subgraph(name='cluster_prepare_legumes_rice') as legume_rice_prep:
    legume_rice_prep.attr(label='Prepare Legumes and Rice', fontname="Helvetica", fontsize="14", fontweight="bold", style="dashed", pencolor="gray")
    legume_rice_prep.node('Drain and Rinse Lentils and Chickpeas', 'Drain and Rinse\nLentils and Chickpeas', shape='ellipse', style="rounded, filled", fillcolor=action_color("Drain"), fontname="Helvetica", fontsize="12")
    legume_rice_prep.node('Rinse Rice', 'Rinse Rice', shape='ellipse', style="rounded, filled", fillcolor=action_color("Rinse"), fontname="Helvetica", fontsize="12")
    legume_rice_prep.node('Lentils', '1 (15-oz) Can Lentils', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Lentils"), fontname="Helvetica", fontsize="12")
    legume_rice_prep.node('Chickpeas', '1 (15-oz) Can Chickpeas', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Chickpeas"), fontname="Helvetica", fontsize="12")
    legume_rice_prep.node('Rice', '1/4 Cup Uncooked\nLong-Grain Rice', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Rice"), fontname="Helvetica", fontsize="12")

    legume_rice_prep.edge('Lentils', 'Drain and Rinse Lentils and Chickpeas', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    legume_rice_prep.edge('Chickpeas', 'Drain and Rinse Lentils and Chickpeas', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    legume_rice_prep.edge('Rice', 'Rinse Rice', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# --- Soup Base Subgraph ---
with dot.subgraph(name='cluster_soup_base') as soup_base:
    soup_base.attr(label='Soup Base', fontname="Helvetica", fontsize="14", fontweight="bold", style="dashed", pencolor="gray")
    soup_base.node('Heat Oil', 'Heat 1 tbsp Olive Oil', shape='oval', style="rounded, filled", fillcolor=action_color("Heat"), fontname="Helvetica", fontsize="12")
    soup_base.node('Saute Onion and Celery', 'Saute Onion and Celery\n(5-7 min)', shape='oval', style="rounded, filled", fillcolor=action_color("Saute"), fontname="Helvetica", fontsize="12")
    soup_base.node('Cook Garlic', 'Cook Garlic (1 min)', shape='oval', style="rounded, filled", fillcolor=action_color("Cook"), fontname="Helvetica", fontsize="12")
    soup_base.node('Olive Oil', '1 tbsp Olive Oil', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Olive Oil"), fontname="Helvetica", fontsize="12")

    soup_base.edge('Olive Oil', 'Heat Oil', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    soup_base.edge('Heat Oil', 'Saute Onion and Celery', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    soup_base.edge('Chop Onion and Celery', 'Saute Onion and Celery', style='solid', label='add to', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    soup_base.edge('Saute Onion and Celery', 'Cook Garlic', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    soup_base.edge('Mince Garlic', 'Cook Garlic', style='solid', label='add to', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")

# --- Build Flavor Subgraph ---
with dot.subgraph(name='cluster_build_flavor') as build_flavor:
    build_flavor.attr(label='Build Flavor', fontname="Helvetica", fontsize="14", fontweight="bold", style="dashed", pencolor="gray")
    build_flavor.node('Add Spices', 'Add Tomato Paste, Ginger,\nTurmeric, Cinnamon, Black Pepper,\nCayenne (1-2 min)', shape='diamond', style="rounded, filled", fillcolor=action_color("Add Spices"), fontname="Helvetica", fontsize="12")
    build_flavor.node('Tomato Paste', '1 tbsp Tomato Paste', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Tomato Paste"), fontname="Helvetica", fontsize="12")
    build_flavor.node('Ginger', '1 tsp Ground Ginger', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Ginger"), fontname="Helvetica", fontsize="12")
    build_flavor.node('Turmeric', '1 tsp Ground Turmeric', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Turmeric"), fontname="Helvetica", fontsize="12")
    build_flavor.node('Cinnamon', '1/2 tsp Ground Cinnamon', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Cinnamon"), fontname="Helvetica", fontsize="12")
    build_flavor.node('Black Pepper', '1/4 tsp Black Pepper', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Black Pepper"), fontname="Helvetica", fontsize="12", fontcolor="white")
    build_flavor.node('Cayenne', 'Pinch of Cayenne Pepper\n(optional)', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Cayenne"), fontname="Helvetica", fontsize="12")

    build_flavor.edge('Tomato Paste', 'Add Spices', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    build_flavor.edge('Ginger', 'Add Spices', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    build_flavor.edge('Turmeric', 'Add Spices', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    build_flavor.edge('Cinnamon', 'Add Spices', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    build_flavor.edge('Black Pepper', 'Add Spices', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    build_flavor.edge('Cayenne', 'Add Spices', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    build_flavor.edge('Cook Garlic', 'Add Spices', style='solid', label='add to', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")

# --- Combine and Simmer Subgraph ---
with dot.subgraph(name='cluster_combine_simmer') as combine_simmer:
    combine_simmer.attr(label='Combine and Simmer', fontname="Helvetica", fontsize="14", fontweight="bold", style="dashed", pencolor="gray")
    combine_simmer.node('Add Liquids and Legumes', 'Add Diced Tomatoes,\nBroth, Lentils, Chickpeas', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    combine_simmer.node('Simmer', 'Simmer (15 min)', shape='house', style="rounded, filled", fillcolor=action_color("Simmer"), fontname="Helvetica", fontsize="12")
    combine_simmer.node('Diced Tomatoes', '1 (14.5 oz) Can\nDiced Tomatoes', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Diced Tomatoes"), fontname="Helvetica", fontsize="12")
    combine_simmer.node('Broth', '6 Cups Vegetable Broth', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Broth"), fontname="Helvetica", fontsize="12")

    combine_simmer.edge('Diced Tomatoes', 'Add Liquids and Legumes', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    combine_simmer.edge('Broth', 'Add Liquids and Legumes', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    combine_simmer.edge('Drain and Rinse Lentils and Chickpeas', 'Add Liquids and Legumes', style='solid', label='add to', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    combine_simmer.edge('Add Spices', 'Add Liquids and Legumes', style='solid', label='add to', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    combine_simmer.edge('Add Liquids and Legumes', 'Simmer', style='dashed', label='for 15 minutes', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray", color="skyblue")

# --- Add Rice and Continue Simmering Subgraph ---
with dot.subgraph(name='cluster_add_rice') as add_rice:
    add_rice.attr(label='Add Rice and Simmer', fontname="Helvetica", fontsize="14", fontweight="bold", style="dashed", pencolor="gray")
    add_rice.node('Add Rice', 'Add Rinsed Rice', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    add_rice.node('Simmer Rice', 'Simmer (15-20 min)', shape='house', style="rounded, filled", fillcolor=action_color("Simmer"), fontname="Helvetica", fontsize="12")

    add_rice.edge('Simmer', 'Add Rice', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    add_rice.edge('Rinse Rice', 'Add Rice', style='solid', label='add to', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    add_rice.edge('Add Rice', 'Simmer Rice', style='dashed', label='for 15-20 minutes', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray", color="skyblue")

# --- Finish and Serve Subgraph ---
with dot.subgraph(name='cluster_finish_serve') as finish_serve:
    finish_serve.attr(label='Finish and Serve', fontname="Helvetica", fontsize="14", fontweight="bold", style="dashed", pencolor="gray")
    finish_serve.node('Add Herbs', 'Add Cilantro and Parsley', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    finish_serve.node('Serve', 'Serve Hot\nwith Lemon Wedges', shape='doublecircle', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    finish_serve.node('Cilantro', '1/2 Cup Chopped Cilantro', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Cilantro"), fontname="Helvetica", fontsize="12")
    finish_serve.node('Parsley', '1/4 Cup Chopped Parsley', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Parsley"), fontname="Helvetica", fontsize="12")
    finish_serve.node('Lemon Wedges', 'Lemon Wedges', shape='ellipse', style="rounded, filled", fillcolor=ingredient_color("Lemon"), fontname="Helvetica", fontsize="12")

    finish_serve.edge('Cilantro', 'Add Herbs', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    finish_serve.edge('Parsley', 'Add Herbs', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    finish_serve.edge('Simmer Rice', 'Add Herbs', style='solid', label='stir in', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    finish_serve.edge('Add Herbs', 'Serve', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    finish_serve.edge('Lemon Wedges', 'Serve', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

dot.render("recipe_flow", view=False, format="pdf")
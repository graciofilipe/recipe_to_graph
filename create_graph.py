import graphviz

dot = graphviz.Digraph(comment='Harira Soup Recipe')
dot.graph_attr['layout'] = 'dot'
dot.graph_attr['rankdir'] = 'TB'
dot.graph_attr['nodesep'] = '0.7'
dot.graph_attr['ranksep'] = '1.0'

def ingredient_node(dot, name, label, color):
    dot.node(name, label, shape='ellipse', style='rounded, filled', fillcolor=color, fontname="Helvetica", fontsize="12")

def prep_action_node(dot, name, label, color='lightblue'):
    dot.node(name, label, shape='parallelogram', style='rounded, filled', fillcolor=color, fontname="Helvetica", fontsize="12")

def mix_action_node(dot, name, label, color='lightsalmon'):
    dot.node(name, label, shape='diamond', style='rounded, filled', fillcolor=color, fontname="Helvetica", fontsize="12")

def cook_action_node(dot, name, label, color='coral'):
    dot.node(name, label, shape='oval', style='rounded, filled', fillcolor=color, fontname="Helvetica", fontsize="12")

def serve_action_node(dot, name, label, color='palegreen'):
    dot.node(name, label, shape='doublecircle', style='rounded, filled', fillcolor=color, fontname="Helvetica", fontsize="12")

# --- Preparation Subgraph ---
with dot.subgraph(name='cluster_preparation') as prep:
    prep.attr(label='Preparation', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    ingredient_node(prep, 'Lentils', 'Lentils\n(15-ounce / 425g can)', 'lightgreen')
    ingredient_node(prep, 'Chickpeas', 'Chickpeas\n(15-ounce / 425g can)', 'lightyellow')
    prep_action_node(prep, 'Drain and Rinse Lentils', 'Drain and Rinse Lentils', 'powderblue')
    prep_action_node(prep, 'Drain and Rinse Chickpeas', 'powderblue')
    ingredient_node(prep, 'Cilantro', 'Fresh Cilantro\n(1/4 cup)', 'palegreen')
    ingredient_node(prep, 'Parsley', 'Fresh Parsley\n(1/4 cup)', 'palegreen')
    prep_action_node(prep, 'Chop Cilantro and Parsley', 'Chop Cilantro and Parsley')

    prep.edge('Lentils', 'Drain and Rinse Lentils', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", color="powderblue")
    prep.edge('Chickpeas', 'Drain and Rinse Chickpeas', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", color="powderblue")
    prep.edge('Cilantro', 'Chop Cilantro and Parsley', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    prep.edge('Parsley', 'Chop Cilantro and Parsley', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# --- Sautéing Aromatics Subgraph ---
with dot.subgraph(name='cluster_sauteing') as saute:
    saute.attr(label='Sautéing Aromatics', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    ingredient_node(saute, 'Olive Oil', 'Olive Oil\n(1 tbsp)', 'lightyellow')
    ingredient_node(saute, 'Onion', 'Onion\n(1 large)', 'lightyellow')
    ingredient_node(saute, 'Celery', 'Celery\n(2 stalks)', 'lightgreen')
    prep_action_node(saute, 'Chop Onion and Celery', 'Chop Onion and Celery', 'palegreen')
    prep_action_node(saute, 'Heat Oil', 'Heat Olive Oil\nin Large Pot', 'lightsalmon')
    cook_action_node(saute, 'Saute Onion and Celery', 'Saute Onion and Celery\n(5-7 minutes)', 'coral')

    saute.edge('Olive Oil', 'Heat Oil', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    saute.edge('Onion', 'Chop Onion and Celery', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    saute.edge('Celery', 'Chop Onion and Celery', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    saute.edge('Chop Onion and Celery', 'Saute Onion and Celery', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    saute.edge('Heat Oil', 'Saute Onion and Celery', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# --- Blooming Spices Subgraph ---
with dot.subgraph(name='cluster_blooming') as bloom:
    bloom.attr(label='Blooming Spices', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    ingredient_node(bloom, 'Garlic', 'Garlic\n(4 cloves)', 'lightyellow')
    prep_action_node(bloom, 'Mince Garlic', 'Mince Garlic')
    ingredient_node(bloom, 'Spices', 'Ginger (1 tsp)\nTurmeric (1 tsp)\nCinnamon (1/2 tsp)\nBlack Pepper (1/2 tsp)\nCayenne (1/4 tsp, optional)', 'yellow')
    mix_action_node(bloom, 'Add Spices and Garlic', 'Add Minced Garlic and Spices\nto Pot')
    cook_action_node(bloom, 'Cook Spices', 'Cook Spices\n(1 minute)')

    bloom.edge('Garlic', 'Mince Garlic', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    bloom.edge('Mince Garlic', 'Add Spices and Garlic', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    bloom.edge('Spices', 'Add Spices and Garlic', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    bloom.edge('Add Spices and Garlic', 'Cook Spices', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    bloom.edge('Saute Onion and Celery', 'Add Spices and Garlic', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# --- Combining and Simmering Subgraph ---
with dot.subgraph(name='cluster_simmering') as simmer:
    simmer.attr(label='Combining and Simmering', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    ingredient_node(simmer, 'Crushed Tomatoes', 'Crushed Tomatoes\n(14.5 ounce / 411g can)', 'lightcoral')
    ingredient_node(simmer, 'Tomato Paste', 'Tomato Paste\n(2 tbsp)', 'tomato')
    ingredient_node(simmer, 'Vegetable Broth', 'Vegetable Broth\n(6-8 cups)', 'powderblue')
    ingredient_node(simmer, 'Rice', 'Long Grain Rice\n(1/4 cup)', 'cornsilk')
    mix_action_node(simmer, 'Combine Ingredients', 'Combine Crushed Tomatoes,\nTomato Paste, Broth, and Rice\nwith Lentils and Chickpeas')
    cook_action_node(simmer, 'Simmer Soup', 'Simmer Soup\n(20-25 minutes)', 'skyblue')

    simmer.edge('Crushed Tomatoes', 'Combine Ingredients', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    simmer.edge('Tomato Paste', 'Combine Ingredients', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    simmer.edge('Vegetable Broth', 'Combine Ingredients', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    simmer.edge('Rice', 'Combine Ingredients', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    simmer.edge('Drain and Rinse Lentils', 'Combine Ingredients', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    simmer.edge('Drain and Rinse Chickpeas', 'Combine Ingredients', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    simmer.edge('Cook Spices', 'Combine Ingredients', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    simmer.edge('Combine Ingredients', 'Simmer Soup', style='dashed', label='until rice is cooked', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray", color="skyblue")

# --- Finishing and Serving Subgraph ---
with dot.subgraph(name='cluster_serving') as serve:
    serve.attr(label='Finishing and Serving', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    ingredient_node(serve, 'Lemon Wedges', 'Lemon Wedges', 'lightyellow')
    mix_action_node(serve, 'Stir in Herbs', 'Stir in Chopped\nCilantro and Parsley')
    serve_action_node(serve, 'Serve', 'Serve Hot\nwith Lemon Wedges')

    serve.edge('Chop Cilantro and Parsley', 'Stir in Herbs', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    serve.edge('Simmer Soup', 'Stir in Herbs', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    serve.edge('Stir in Herbs', 'Serve', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    serve.edge('Lemon Wedges', 'Serve', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

dot.render("recipe_flow", view=False, format="pdf")
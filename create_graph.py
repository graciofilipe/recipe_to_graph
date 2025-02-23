import graphviz

# Create a directed graph for the Zaalouk recipe
zaalouk = graphviz.Digraph(comment='Zaalouk Recipe', graph_attr={'rankdir': 'TB', 'dpi':'300'})

# --- Tomato Base Preparation ---
zaalouk.attr('node', shape='box', style='filled', color='lightcoral')

zaalouk.node("Tomatoes", "Peel, seed, and chop Tomatoes")
zaalouk.node("Spices", "Gather Spices, Garlic, and Herbs")
zaalouk.node("Combine1", "Combine Tomatoes, Olive Oil,\nSpices, Garlic, and Herbs in skillet",  shape='oval')

zaalouk.edge("Tomatoes", "Combine1")
zaalouk.edge("Spices", "Combine1")

# --- Eggplant Preparation ---
zaalouk.attr('node', shape='box', style='filled', color='mediumpurple')

zaalouk.node("Eggplants", "Trim and peel Eggplants")
zaalouk.node("ChopEggplants", "Finely chop Eggplants")
zaalouk.node("Combine2", "Add Eggplants and Water to skillet", shape='oval')

zaalouk.edge("Eggplants", "ChopEggplants")
zaalouk.edge("ChopEggplants", "Combine2")

# --- Cooking Process ---
zaalouk.attr('node', shape='ellipse', style='filled', color='lightgreen')

zaalouk.node("Cook1", "Cover and cook for 10-15 mins,\nuntil eggplant softens")
zaalouk.node("Stir", "Stir to combine all ingredients")
zaalouk.node("Cook2", "Add chili/cayenne (optional),\nmore water (if needed),\ncover and cook for 15-20 mins,\nuntil eggplant and tomatoes are soft")
zaalouk.node("Reduce", "Cook uncovered to reduce liquids,\nstirring frequently,\nmash (optional)")
zaalouk.node("Serve", "Taste, adjust seasoning, and serve with bread", shape='box')

zaalouk.edge("Combine1", "Cook1")
zaalouk.edge("Combine2", "Cook1")
zaalouk.edge("Cook1", "Stir")
zaalouk.edge("Stir", "Cook2")
zaalouk.edge("Cook2", "Reduce")
zaalouk.edge("Reduce", "Serve")

# Render the graph to a file
zaalouk.render('zaalouk_recipe', view=False, format='png')
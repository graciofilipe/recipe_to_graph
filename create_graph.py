import graphviz

dot = graphviz.Digraph(comment='Zaalouk Recipe Flow')

dot.attr(rankdir='TB', fontname="Arial")

with dot.subgraph(name='cluster_ingredients') as c:
    c.attr(style='filled', color='lightgrey', label='Ingredients', fontname="Arial")
    c.node_attr.update(style='filled', color='white', fontname="Arial")
    c.node('Eggplants', '2 Large Eggplants', shape='rectangle')
    c.node('Tomatoes', '2 Medium/Large Tomatoes', shape='rectangle')
    c.node('Garlic', '6 Cloves Garlic', shape='rectangle')
    c.node('Parsley', '2 Tbsp Fresh Parsley', shape='rectangle')
    c.node('Cilantro', '2 Tbsp Fresh Cilantro', shape='rectangle')
    c.node('Spices', 'Salt, Paprika, Cumin', shape='rectangle')
    c.node('Olive Oil', '4 Tbsp Olive Oil', shape='rectangle')
    c.node('Water', '1/4 - 1/3 Cup Water', shape='rectangle')
    c.node('Optional', 'Cayenne Pepper, Lemon Juice', shape='rectangle')

with dot.subgraph(name='cluster_prep') as c:
    c.attr(style='filled', color='lightgrey', label='Preparation', fontname="Arial")
    c.node_attr.update(style='filled', color='white', fontname="Arial")
    c.edge_attr.update(fontname="Arial")
    c.node('Chop_Tomatoes', 'Chop Tomatoes', shape='rectangle', fillcolor='red')
    c.node('Press_Garlic', 'Press Garlic', shape='rectangle', fillcolor='lightyellow')
    c.node('Chop_Parsley', 'Chop Parsley', shape='rectangle', fillcolor='green')
    c.node('Chop_Cilantro', 'Chop Cilantro', shape='rectangle', fillcolor='green')
    c.node('Peel_Eggplants', 'Peel Eggplants', shape='rectangle', fillcolor='purple')
    c.node('Chop_Eggplants', 'Chop Eggplants', shape='rectangle', fillcolor='purple')

    c.edge('Tomatoes', 'Chop_Tomatoes')
    c.edge('Garlic', 'Press_Garlic')
    c.edge('Parsley', 'Chop_Parsley')
    c.edge('Cilantro', 'Chop_Cilantro')
    c.edge('Eggplants', 'Peel_Eggplants')
    c.edge('Peel_Eggplants', 'Chop_Eggplants')

with dot.subgraph(name='cluster_cook') as c:
    c.attr(style='filled', color='lightgrey', label='Cooking', fontname="Arial")
    c.node_attr.update(style='filled', color='white', fontname="Arial", shape='oval')
    c.edge_attr.update(fontname="Arial")
    c.node('Combine1', 'Combine Ingredients in Skillet', shape='diamond')
    c.node('Cook1', 'Cook 10-15 min', shape='oval')
    c.node('Combine2', 'Stir to Combine', shape='diamond')
    c.node('Cook2', 'Cook 15-20 min', shape='oval')
    c.node('Reduce', 'Reduce Liquids', shape='oval')
    c.node('Zaalouk', 'Zaalouk', shape='ellipse')

    c.edge('Chop_Tomatoes', 'Combine1')
    c.edge('Press_Garlic', 'Combine1')
    c.edge('Chop_Parsley', 'Combine1')
    c.edge('Chop_Cilantro', 'Combine1')
    c.edge('Spices', 'Combine1')
    c.edge('Olive Oil', 'Combine1')
    c.edge('Chop_Eggplants', 'Combine1')
    c.edge('Water', 'Combine1')
    c.edge('Combine1', 'Cook1')
    c.edge('Cook1', 'Combine2')
    c.edge('Combine2', 'Cook2')
    c.edge('Optional', 'Cook2', label='add if using')
    c.edge('Cook2', 'Reduce')
    c.edge('Reduce', 'Zaalouk')

dot.render('zaalouk_recipe_flow', view=False, format='pdf')
import graphviz

dot = graphviz.Digraph(comment='Zaalouk Recipe Flow')

dot.attr(rankdir='TB')

with dot.subgraph(name='cluster_ingredients') as c:
    c.attr(style='filled', color='lightgrey', label='Ingredients', fontname="Arial")
    c.node_attr.update(style='filled', shape='rect', fontname="Arial")
    c.node('Eggplants', '2 Large Eggplants', color='purple')
    c.node('Tomatoes', '2 Medium/Large Tomatoes', color='red')
    c.node('Garlic', '6 Cloves Garlic', color='lightyellow')
    c.node('Parsley', '2 Tbsp Fresh Parsley', color='green')
    c.node('Cilantro', '2 Tbsp Fresh Cilantro', color='green')
    c.node('Spices', '1 tsp Salt\n2 tsp Paprika\n2 tsp Cumin\nCayenne Pepper (optional)', color='orange')
    c.node('Olive Oil', '4 Tbsp Olive Oil', color='yellow')
    c.node('Water', '1/4 - 1/3 Cup Water', color='lightblue')
    c.node('Lemon Juice', 'Lemon Juice (optional)', color='lightyellow')

with dot.subgraph(name='cluster_prep') as c:
    c.attr(style='filled', color='lightgrey', label='Preparation', fontname="Arial")
    c.node_attr.update(style='filled', fontname="Arial")
    c.edge_attr.update(fontname="Arial")

    c.node('Chop Tomatoes', 'Chop Tomatoes', shape='parallelogram', color='red')
    c.edge('Tomatoes', 'Chop Tomatoes')

    c.node('Press Garlic', 'Press Garlic', shape='parallelogram', color='lightyellow')
    c.edge('Garlic', 'Press Garlic')

    c.node('Chop Parsley', 'Chop Parsley', shape='parallelogram', color='green')
    c.edge('Parsley', 'Chop Parsley')

    c.node('Chop Cilantro', 'Chop Cilantro', shape='parallelogram', color='green')
    c.edge('Cilantro', 'Chop Cilantro')

    c.node('Peel and Chop Eggplants', 'Peel and Chop Eggplants', shape='parallelogram', color='purple')
    c.edge('Eggplants', 'Peel and Chop Eggplants')

with dot.subgraph(name='cluster_cook') as c:
    c.attr(style='filled', color='lightgrey', label='Cooking', fontname="Arial")
    c.node_attr.update(style='filled', fontname="Arial", color='white')
    c.edge_attr.update(fontname="Arial")

    c.node('Combine Initial', 'Combine in Skillet/Pot', shape='diamond')
    c.edge('Chop Tomatoes', 'Combine Initial', label='add to')
    c.edge('Press Garlic', 'Combine Initial', label='add to')
    c.edge('Chop Parsley', 'Combine Initial', label='add to')
    c.edge('Chop Cilantro', 'Combine Initial', label='add to')
    c.edge('Spices', 'Combine Initial', label='add to')
    c.edge('Olive Oil', 'Combine Initial', label='add to')

    c.node('Add Eggplants', 'Add Eggplants and Water')
    c.edge('Combine Initial', 'Add Eggplants', label='add to')
    c.edge('Peel and Chop Eggplants', 'Add Eggplants', label='add to')
    c.edge('Water', 'Add Eggplants', label='add to')

    c.node('Cook 1', 'Cook Covered (10-15 min)', shape='oval', color='orange')
    c.edge('Add Eggplants', 'Cook 1')

    c.node('Stir', 'Stir to Combine')
    c.edge('Cook 1', 'Stir')

    c.node('Cook 2', 'Cook Covered (15-20 min)', shape='oval', color='orange')
    c.edge('Stir', 'Cook 2')
    c.edge('Lemon Juice', 'Cook 2', label='add (optional)')

    c.node('Reduce Liquid', 'Reduce Liquid, Stirring Frequently', shape='oval', color='orange')
    c.edge('Cook 2', 'Reduce Liquid')

    c.node('Mash', 'Mash (optional)', shape='diamond')
    c.edge('Reduce Liquid', 'Mash')

    c.node('Cook Final', 'Continue Cooking to Desired Consistency', shape='oval', color='orange')
    c.edge('Mash', 'Cook Final')

    c.node('Zaalouk', 'Zaalouk', shape='rectangle', color='brown')
    c.edge('Cook Final', 'Zaalouk')

dot.render('zaalouk_recipe_flow', view=False, format='pdf')
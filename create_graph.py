import graphviz

dot = graphviz.Digraph(comment='Cavolo Nero and Butter Bean Soup Recipe')
dot.graph_attr['rankdir'] = 'TB'
dot.graph_attr['nodesep'] = '0.75'
dot.graph_attr['ranksep'] = '1.0'

ingredient_colors = {
    'onion': '#FFFACD',
    'carrot': '#FFDEAD',
    'garlic': '#F0FFF0',
    'cavolo nero': '#98FB98',
    'butter beans': '#FAEBD7',
    'vegetable stock': '#E0FFFF',
    'olive oil': '#FFFFE0',
}

action_colors = {
    'chop': '#D3D3D3',
    'cut': '#D3D3D3',
    'saute': '#FFA07A',
    'cook': '#F08080',
    'boil': '#87CEFA',
    'blend': '#DDA0DD',
    'season': '#FFB6C1',
    'add': '#AFEEEE',
    'combine': '#AFEEEE',
    'drain': '#D3D3D3',
    'measure': '#D3D3D3',
}

with dot.subgraph(name='cluster_ingredients') as c:
    c.attr(label='Ingredients')
    c.attr(fontname="Helvetica")
    c.attr(fontweight="bold")
    c.node('Onion', '1 Onion', shape='box', style='filled', fillcolor=ingredient_colors['onion'], fontname='Helvetica')
    c.node('Carrot', '1 Carrot', shape='box', style='filled', fillcolor=ingredient_colors['carrot'], fontname='Helvetica')
    c.node('Garlic', '1 Garlic clove', shape='box', style='filled', fillcolor=ingredient_colors['garlic'], fontname='Helvetica')
    c.node('Cavolo Nero', '200g Cavolo Nero', shape='box', style='filled', fillcolor=ingredient_colors['cavolo nero'], fontname='Helvetica')
    c.node('Butter Beans', '1 Can Butter Beans', shape='box', style='filled', fillcolor=ingredient_colors['butter beans'], fontname='Helvetica')
    c.node('Vegetable Stock', '600ml Vegetable Stock', shape='box', style='filled', fillcolor=ingredient_colors['vegetable stock'], fontname='Helvetica')
    c.node('Olive Oil', '2 tbsp Olive Oil', shape='box', style='filled', fillcolor=ingredient_colors['olive oil'], fontname='Helvetica')


with dot.subgraph(name='cluster_cooking') as c:
    c.attr(fontname="Helvetica")
    c.attr(fontweight="bold")
    label = c.name.split('cluster_')[-1].replace('_', ' ').title()
    c.attr(label=label)

    c.node('Prepare Onion', 'Chop Onion', shape='box', style='filled', fillcolor='#FAF0E6', fontname='Helvetica')
    c.node('Prepare Carrot', 'Cut Carrot into small cubes', shape='box', style='filled', fillcolor='#FFE4B5', fontname='Helvetica')
    c.node('Prepare Garlic', 'Chop Garlic clove', shape='box', style='filled', fillcolor='#F5FFFA', fontname='Helvetica')
    c.node('Prepare Cavolo Nero', 'Roughly chop leaves, finely chop stems', shape='box', style='filled', fillcolor='#C1FFC1', fontname='Helvetica')
    c.node('Drain Butter Beans', 'Drain Butter Beans', shape='box', style='filled', fillcolor='#FAF0E6', fontname='Helvetica')
    c.node('Saute Vegetables', 'Saute Onion, Carrot, and Garlic in Olive Oil', shape='ellipse', style='filled', fillcolor=action_colors['saute'], fontname='Helvetica')
    c.node('Season Vegetables', 'Season with Chilli flakes, Salt, and Pepper', shape='ellipse', style='filled', fillcolor=action_colors['season'], fontname='Helvetica')
    c.node('Cook Vegetables', 'Cook for 8-10 minutes until fragrant', shape='ellipse', style='filled', fillcolor=action_colors['cook'], fontname='Helvetica')
    c.node('Add Ingredients', 'Add Stock and Butter Beans', shape='ellipse', style='filled', fillcolor=action_colors['add'], fontname='Helvetica')
    c.node('Boil Soup', 'Bring to a boil', shape='ellipse', style='filled', fillcolor=action_colors['boil'], fontname='Helvetica')
    c.node('Cook Soup 2', 'Cook for 8-10 minutes until vegetables are tender', shape='ellipse', style='filled', fillcolor=action_colors['cook'], fontname='Helvetica')
    c.node('Blend Soup', 'Blend half of the soup mixture until smooth', shape='ellipse', style='filled', fillcolor=action_colors['blend'], fontname='Helvetica')
    c.node('Combine Soup', 'Pour blended mixture back into pan', shape='ellipse', style='filled', fillcolor=action_colors['combine'], fontname='Helvetica')
    c.node('Add Cavolo Nero', 'Add Cavolo Nero', shape='ellipse', style='filled', fillcolor=action_colors['add'], fontname='Helvetica')
    c.node('Cook Soup 3', 'Cook for 5 minutes until Cavolo Nero softens', shape='ellipse', style='filled', fillcolor=action_colors['cook'], fontname='Helvetica')

dot.edge('Prepare Onion', 'Saute Vegetables', label='add to pan', arrowhead='normal', fontname='Helvetica')
dot.edge('Prepare Carrot', 'Saute Vegetables', label='add to pan', arrowhead='normal', fontname='Helvetica')
dot.edge('Prepare Garlic', 'Saute Vegetables', label='add to pan', arrowhead='normal', fontname='Helvetica')
dot.edge('Saute Vegetables', 'Season Vegetables', arrowhead='normal', fontname='Helvetica')
dot.edge('Season Vegetables','Cook Vegetables', arrowhead='normal', fontname='Helvetica')
dot.edge('Cook Vegetables', 'Add Ingredients', label='add to', arrowhead='normal', fontname='Helvetica')
dot.edge('Vegetable Stock', 'Add Ingredients', label='add to', arrowhead='normal', fontname='Helvetica')
dot.edge('Butter Beans', 'Add Ingredients', label='add to', arrowhead='normal', fontname='Helvetica')
dot.edge('Add Ingredients', 'Boil Soup', arrowhead='normal', fontname='Helvetica')
dot.edge('Boil Soup', 'Cook Soup 2', arrowhead='normal', fontname='Helvetica')
dot.edge('Cook Soup 2', 'Blend Soup', arrowhead='normal', fontname='Helvetica')
dot.edge('Blend Soup', 'Combine Soup', arrowhead='normal', fontname='Helvetica')
dot.edge('Combine Soup', 'Add Cavolo Nero', label='add to', arrowhead='normal', fontname='Helvetica')
dot.edge('Prepare Cavolo Nero', 'Add Cavolo Nero', label='add to', arrowhead='normal', fontname='Helvetica')
dot.edge('Add Cavolo Nero', 'Cook Soup 3', arrowhead='normal', fontname='Helvetica')

dot.render("recipe_flow", view=False, format="pdf")
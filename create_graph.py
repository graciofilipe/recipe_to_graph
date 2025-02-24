import graphviz

dot = graphviz.Digraph(graph_attr={'rankdir': 'TB', 'nodesep': '0.7', 'ranksep': '1.0', 'layout': 'dot'})

# Cabbage Preparation
with dot.subgraph(name='cluster_cabbage_prep') as c:
    c.attr(label='Cabbage Preparation', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    c.node('cabbage', '6-8 Napa Cabbage Leaves', shape='ellipse', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    c.node('separate', 'Separate Leaves', shape='parallelogram', style="rounded, filled", fillcolor="lightblue", fontname="Helvetica", fontsize="12")
    c.node('pound', 'Pound Stems', shape='parallelogram', style="rounded, filled", fillcolor="lightblue", fontname="Helvetica", fontsize="12")
    c.edge('cabbage', 'separate', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    c.edge('separate', 'pound', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# Batter Preparation
with dot.subgraph(name='cluster_batter_prep') as b:
    b.attr(label='Batter Preparation', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    b.node('flour', '1 cup Flour', shape='ellipse', style="rounded, filled", fillcolor="lightyellow", fontname="Helvetica", fontsize="12")
    b.node('water', '1 cup Water', shape='ellipse', style="rounded, filled", fillcolor="powderblue", fontname="Helvetica", fontsize="12")
    b.node('egg', '1 Egg (optional)', shape='ellipse', style="rounded, filled", fillcolor="lemonchiffon", fontname="Helvetica", fontsize="12")
    b.node('starch', '2 tbsp Potato Starch', shape='ellipse', style="rounded, filled", fillcolor="lightyellow", fontname="Helvetica", fontsize="12")
    b.node('salt', '1 tsp Salt', shape='ellipse', style="rounded, filled", fillcolor="gainsboro", fontname="Helvetica", fontsize="12")
    b.node('mix_batter', 'Mix Batter', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    b.edge('flour', 'mix_batter', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    b.edge('water', 'mix_batter', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    b.edge('egg', 'mix_batter', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    b.edge('starch', 'mix_batter', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    b.edge('salt', 'mix_batter', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    b.node('batter', 'Batter', shape='ellipse', style="rounded, filled", fillcolor="palegoldenrod", fontname="Helvetica", fontsize="12")
    b.edge('mix_batter', 'batter', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# Dipping Sauce Preparation
with dot.subgraph(name='cluster_sauce_prep') as s:
    s.attr(label='Dipping Sauce Preparation', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    s.node('soy_sauce', 'Soy Sauce', shape='ellipse', style="rounded, filled", fillcolor="skyblue", fontname="Helvetica", fontsize="12")
    s.node('vinegar', 'White Vinegar', shape='ellipse', style="rounded, filled", fillcolor="powderblue", fontname="Helvetica", fontsize="12")
    s.node('sesame', 'Sesame Seeds', shape='ellipse', style="rounded, filled", fillcolor="lightyellow", fontname="Helvetica", fontsize="12")
    s.node('gochugaru', 'Gochugaru', shape='ellipse', style="rounded, filled", fillcolor="orangered", fontname="Helvetica", fontsize="12")
    s.node('mix_sauce', 'Mix Sauce', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    s.edge('soy_sauce', 'mix_sauce', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    s.edge('vinegar', 'mix_sauce', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    s.edge('sesame', 'mix_sauce', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    s.edge('gochugaru', 'mix_sauce', label='combine', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    s.node('sauce', 'Dipping Sauce', shape='doublecircle', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    s.edge('mix_sauce', 'sauce', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# Frying
with dot.subgraph(name='cluster_frying') as f:
    f.attr(label='Frying', fontname="Helvetica", fontweight="bold", fontsize="14", style="dashed", pencolor="gray")
    f.node('oil', 'Vegetable Oil', shape='ellipse', style="rounded, filled", fillcolor="lightyellow", fontname="Helvetica", fontsize="12")
    f.node('heat_pan', 'Heat Pan (Medium Heat)', shape='house', style="rounded, filled", fillcolor="skyblue", fontname="Helvetica", fontsize="12")
    f.node('dip', 'Dip Cabbage in Batter', shape='diamond', style="rounded, filled", fillcolor="lightsalmon", fontname="Helvetica", fontsize="12")
    f.node('fry', 'Fry (2-3 min/side)', shape='oval', style="rounded, filled", fillcolor="coral", fontname="Helvetica", fontsize="12")
    f.edge('oil', 'heat_pan', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    f.edge('heat_pan', 'dip', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    f.edge('pound', 'dip', label='use', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    f.edge('batter', 'dip', label='use', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
    f.edge('dip', 'fry', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")
    f.node('fried_cabbage', 'Fried Cabbage', shape='doublecircle', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
    f.edge('fry', 'fried_cabbage', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8")

# Serving
dot.node('serve', 'Serve Warm', shape='doublecircle', style="rounded, filled", fillcolor="palegreen", fontname="Helvetica", fontsize="12")
dot.edge('fried_cabbage', 'serve', label='with', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")
dot.edge('sauce', 'serve', label='with', arrowhead="normal", arrowsize="0.7", fontname="Helvetica", fontsize="10", penwidth="0.8", labelfontcolor="darkgray")

dot.render("recipe_flow", view=False, format="pdf")
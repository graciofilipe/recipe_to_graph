import graphviz

dot = graphviz.Digraph(comment='Tricolour Recipe', graph_attr={'layout': 'dot', 'nodesep': '0.7', 'ranksep': '1.0', 'rankdir': 'TB'})

# General Node Style
dot.node_attr['fontname'] = 'Helvetica'
dot.node_attr['fontsize'] = '12'
dot.node_attr['style'] = 'rounded, filled'

# General Edge Style
dot.edge_attr['arrowhead'] = 'normal'
dot.edge_attr['arrowsize'] = '0.7'
dot.edge_attr['fontname'] = 'Helvetica'
dot.edge_attr['fontsize'] = '10'
dot.edge_attr['penwidth'] = '0.8'

# Course 1: Tricolour Celebration Cubes

with dot.subgraph(name='cluster_course1') as c1:
    c1.attr(label='Course 1: Tricolour Celebration Cubes')
    c1.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')

    with c1.subgraph(name='cluster_parsnip') as parsnip:
        parsnip.attr(label='Parsnip (White) Layer')
        parsnip.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')
        parsnip.node('Parsnips', '2 Parsnips', shape='ellipse', fillcolor='lightyellow')
        parsnip.node('Cut Parsnips', 'Cut Parsnips\ninto 1-inch cubes', shape='parallelogram', fillcolor='lemonchiffon')
        parsnip.node('Cook Parsnips', 'Steam/Boil Parsnips\n(8-10 min)', shape='house', fillcolor='skyblue')
        parsnip.edge('Parsnips', 'Cut Parsnips')
        parsnip.edge('Cut Parsnips', 'Cook Parsnips')
        parsnip.node('Ice Water Bath', 'Transfer to\nIce Water', shape='Mdiamond', fillcolor='powderblue')
        parsnip.edge('Cook Parsnips', 'Ice Water Bath', style='dashed', label='until tender', color='darkblue')
        parsnip.node('Drain Parsnips', 'Drain Parsnips', shape='diamond', fillcolor='lightsalmon')
        parsnip.edge('Ice Water Bath', 'Drain Parsnips')
        parsnip.node('Season Parsnips', 'Toss with Lemon Juice,\nSalt, White Pepper', shape='diamond', fillcolor='lightsalmon')
        parsnip.edge('Drain Parsnips', 'Season Parsnips')
        parsnip.node('Chill Parsnips', 'Chill Parsnips', shape='component', fillcolor='lightgray')
        parsnip.edge('Season Parsnips', 'Chill Parsnips', style='dashed', color='gray')

    with c1.subgraph(name='cluster_beetroot') as beetroot:
        beetroot.attr(label='Beetroot (Purple) Layer')
        beetroot.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')
        beetroot.node('Beetroots', '2 Beetroots\n(pre-cooked)', shape='ellipse', fillcolor='plum')
        beetroot.node('Cut Beetroots', 'Cut Beetroots\ninto 1-inch cubes', shape='parallelogram', fillcolor='violet')
        beetroot.edge('Beetroots', 'Cut Beetroots')
        beetroot.node('Season Beetroots', 'Toss with Balsamic Vinegar,\nSalt, Pepper', shape='diamond', fillcolor='lightsalmon')
        beetroot.edge('Cut Beetroots', 'Season Beetroots')
        beetroot.node('Chill Beetroots', 'Chill Beetroots', shape='component', fillcolor='lightgray')
        beetroot.edge('Season Beetroots', 'Chill Beetroots', style='dashed', color='gray')

    with c1.subgraph(name='cluster_avocado') as avocado:
        avocado.attr(label='Avocado (Green) Layer')
        avocado.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')
        avocado.node('Avocado', '1 Avocado', shape='ellipse', fillcolor='lightgreen')
        avocado.node('Cut Avocado', 'Cut Avocado\ninto 1-inch cubes', shape='parallelogram', fillcolor='palegreen')
        avocado.edge('Avocado', 'Cut Avocado')
        avocado.node('Season Avocado', 'Toss with Lime Juice,\nSalt, Pepper, Cilantro/Parsley', shape='diamond', fillcolor='lightsalmon')
        avocado.edge('Cut Avocado', 'Season Avocado')
        avocado.node('Chill Avocado', 'Chill Avocado', shape='component', fillcolor='lightgray')
        avocado.edge('Season Avocado', 'Chill Avocado', style='dashed', color='gray')

    c1.node('Assemble Course 1', 'Arrange Cubes\non Platter', shape='doublecircle', fillcolor='palegreen')
    c1.edge('Chill Parsnips', 'Assemble Course 1')
    c1.edge('Chill Beetroots', 'Assemble Course 1')
    c1.edge('Chill Avocado', 'Assemble Course 1')
    c1.node('Serve Course 1', 'Serve Chilled', shape='plaintext', style='')
    c1.edge('Assemble Course 1', 'Serve Course 1', style='dashed')

# Course 2: Tricolour Harmony Plate

with dot.subgraph(name='cluster_course2') as c2:
    c2.attr(label='Course 2: Tricolour Harmony Plate')
    c2.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')

    with c2.subgraph(name='cluster_tofu') as tofu:
        tofu.attr(label='Tofu (White) Preparation')
        tofu.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')
        tofu.node('Tofu', '1 Block Extra-Firm\nTofu (pressed)', shape='ellipse', fillcolor='lightyellow')
        tofu.node('Cut Tofu', 'Cut Tofu\ninto 1-inch cubes', shape='parallelogram', fillcolor='lemonchiffon')
        tofu.edge('Tofu', 'Cut Tofu')
        tofu.node('Season Tofu', 'Toss with Soy Sauce,\nSesame Oil, Garlic Powder,\nOnion Powder, Cornstarch', shape='diamond', fillcolor='lightsalmon')
        tofu.edge('Cut Tofu', 'Season Tofu')
        tofu.node('Cook Tofu', 'Cook in Skillet\n(8-10 min)', shape='oval', fillcolor='orangered')
        tofu.edge('Season Tofu', 'Cook Tofu')
        tofu.node('Set Aside Tofu', 'Set Aside', shape='component', fillcolor='lightgray')
        tofu.edge('Cook Tofu', 'Set Aside Tofu', style='dashed', label='until golden brown', color='orangered')

    with c2.subgraph(name='cluster_spring_greens') as greens:
        greens.attr(label='Spring Greens (Green) Preparation')
        greens.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')
        greens.node('Spring Greens', '1 Bunch\nSpring Greens', shape='ellipse', fillcolor='lightgreen')
        greens.node('Prepare Greens', 'Wash and Chop\nSpring Greens', shape='parallelogram', fillcolor='palegreen')
        greens.edge('Spring Greens', 'Prepare Greens')
        greens.node('Olive Oil', 'Heat Olive Oil', shape='oval', fillcolor='lightcoral')
        greens.node('Cook Garlic', 'Cook Minced Garlic\n(30 sec)', shape='oval', fillcolor='tomato')
        greens.edge('Olive Oil', 'Cook Garlic', style='dashed', label='until fragrant', color='orangered')
        greens.node('Cook Greens', 'Cook Spring Greens\n(3-5 min)', shape='house', fillcolor='skyblue')
        greens.edge('Cook Garlic', 'Cook Greens', color='orangered')
        greens.edge('Prepare Greens', 'Cook Greens')
        greens.node('Set Aside Greens', 'Set Aside', shape='component', fillcolor='lightgray')
        greens.edge('Cook Greens', 'Set Aside Greens', style='dashed', label='until wilted', color='darkblue')

    with c2.subgraph(name='cluster_cabbage') as cabbage:
        cabbage.attr(label='Purple Cabbage (Purple) Preparation')
        cabbage.attr(fontname='Helvetica', fontweight='bold', fontsize='14', style='dashed', pencolor='gray')
        cabbage.node('Purple Cabbage', '1/2 Head\nPurple Cabbage', shape='ellipse', fillcolor='plum')
        cabbage.node('Slice Cabbage', 'Thinly Slice Cabbage', shape='parallelogram', fillcolor='violet')
        cabbage.edge('Purple Cabbage', 'Slice Cabbage')
        cabbage.node('Season Cabbage', 'Combine with Apple Cider Vinegar,\nSugar, Salt, Pepper', shape='diamond', fillcolor='lightsalmon')
        cabbage.edge('Slice Cabbage', 'Season Cabbage')
        cabbage.node('Massage Cabbage', 'Massage Cabbage\n(1-2 min)', shape='hexagon', fillcolor='lightsteelblue')
        cabbage.edge('Season Cabbage', 'Massage Cabbage')
        cabbage.node('Set Aside Cabbage', 'Set Aside', shape='component', fillcolor='lightgray')
        cabbage.edge('Massage Cabbage', 'Set Aside Cabbage', style='dashed', color='gray')

    c2.node('Assemble Course 2', 'Arrange Tofu, Greens,\nand Cabbage on Plates', shape='doublecircle', fillcolor='palegreen')
    c2.edge('Set Aside Tofu', 'Assemble Course 2')
    c2.edge('Set Aside Greens', 'Assemble Course 2')
    c2.edge('Set Aside Cabbage', 'Assemble Course 2')
    c2.node('Serve Course 2', 'Serve Immediately', shape='plaintext', style='')
    c2.edge('Assemble Course 2', 'Serve Course 2')

dot.render("recipe_flow", view=False, format="pdf")
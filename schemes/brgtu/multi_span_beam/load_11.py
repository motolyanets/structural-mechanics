from core.mechanics.node import Node
from core.mechanics.load import Force, DistributedForce


def create_beam_load_11(params: dict):
    a = params["l1"]
    b = params["l2"]
    c = params["h1"]
    d = params["h2"]
    P1 = params["P1"]
    P2 = params["P2"]
    P3 = params["P3"]
    q1 = params["q1"]
    q2 = params["q2"]

    node1 = Node(name='1', x=0, y=0)
    node2 = Node(name='2', x=a * 0.5, y=0)
    node3 = Node(name='3', x=a * 2, y=0)
    node4 = Node(name='4', x=a * 3, y=0)
    node5 = Node(name='5', x=a * 4, y=0)
    node6 = Node(name='6', x=a * 4 + b * 1.5, y=0)
    node7 = Node(name='7', x=a * 4 + b * 2, y=0)
    node8 = Node(name='8', x=a * 4 + b * 4, y=0)
    node9 = Node(name='9', x=(a + b) * 4 + c * 0.5, y=0)
    node10 = Node(name='10', x=(a + b) * 4 + c * 2, y=0)
    node11 = Node(name='11', x=(a + b) * 4 + c * 4, y=0)
    node12 = Node(name='12', x=(a + b + c) * 4 + d * 2, y=0)

    nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12]
    sections_for_diagram = [node6, node9, node11]

    load_1 = Force(name='P3', node=node2, value=P3, rotation=270)
    load_2 = DistributedForce(name='q1', start_coordinates=(node3.x, node3.y), end_coordinates=(node4.x, node4.y), value=q1, rotation=270)
    load_3 = Force(name='P1', node=node5, value=P1, rotation=270)
    load_4 = DistributedForce(name='q1', start_coordinates=(node7.x, node7.y), end_coordinates=(node8.x, node8.y), value=q1, rotation=270)
    load_5 = Force(name='P1', node=node9, value=P1, rotation=270)
    load_6 = DistributedForce(name='q2', start_coordinates=(node10.x, node10.y), end_coordinates=(node12.x, node12.y), value=q2, rotation=270)
    load_7 = Force(name='P3', node=node11, value=P3, rotation=270)
    load_8 = Force(name='P2', node=node12, value=P2, rotation=270)

    loads = [load_1, load_2, load_3, load_4, load_5, load_6, load_7, load_8]

    return nodes, sections_for_diagram, loads

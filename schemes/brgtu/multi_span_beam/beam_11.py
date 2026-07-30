import importlib

from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.support import Support
from schemes.brgtu.multi_span_beam.services import get_beam_load_schema


def create_beam_11(params: dict):
    a = params["a"]
    b = params["b"]
    c = params["c"]
    d = params["d"]
    P1 = params["P1"]
    P2 = params["P2"]
    P3 = params["P3"]
    q1 = params["q1"]
    q2 = params["q2"]

    details = dict()

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='E', x=a * 2, y=0, is_hinge=True)
    node3 = Node(name='B', x=a * 4 + b, y=0)
    node4 = Node(name='T', x=a * 4 + b * 2, y=0, is_hinge=True)
    node5 = Node(name='C', x=(a + b) * 4 + c * 2, y=0)
    node6 = Node(name='S', x=(a + b) * 4 + c * 3, y=0, is_hinge=True)
    node7 = Node(name='D', x=(a + b + c) * 4 + d, y=0)

    nodes = [node1, node2, node3, node4, node5, node6, node7]

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node3, number_of_reactions=1, rotation=90)
    support3 = Support(node=node5, number_of_reactions=1, rotation=90)
    support4 = Support(node=node7, number_of_reactions=1, rotation=90)

    supports = [support1, support2, support3, support4]

    create_beam_load = get_beam_load_schema(load_number=params["load_number"])

    beam_nodes, sections_for_diagram, loads = create_beam_load(params=params, beam_nodes=nodes)

    rods = []
    i = 1
    while True:
        if i == len(beam_nodes):
            break
        rod = Rod(start_node=beam_nodes[i - 1], end_node=beam_nodes[i])
        rods.append(rod)
        i += 1

    details['splitted_frames_order'] = (
        ['S1', 'D'],
        ['T1', 'C', 'S'],
        ['E1', 'B', 'T'],
        ['A', 'E'],
    )

    return beam_nodes, rods, supports, loads, sections_for_diagram, details

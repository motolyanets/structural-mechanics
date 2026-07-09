from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.solver import SolvableFrame
from core.mechanics.support import Support


def create_frame_18(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='2', x=0, y=h1 * 0.5)
    node3 = Node(name='D', x=0, y=h1, is_hinge=True)
    node4 = Node(name='4', x=l2, y=h1 + h2)
    node5 = Node(name='E', x=l2, y=h1)
    node6 = Node(name='6', x=l2, y=h1 * 0.5)
    node7 = Node(name='7', x=l2 * 0.7, y=h1 * 0.5)
    node8 = Node(name='B', x=l2 + l1 * 0.5, y=h1 * 0.5)
    node9 = Node(name='9', x=l2 + l1, y=h1 * 0.5)
    node10 = Node(name='10', x=l2 * 1.3 + l1, y=h1 * 0.5)
    node11 = Node(name='V', x=l2 + l1, y=h1)
    node12 = Node(name='12', x=l2 + l1, y=h1 + h2)
    node13 = Node(name='S', x=l2 * 2 + l1, y=h1, is_hinge=True)
    node14 = Node(name='K', x=l2 * 2 + l1, y=h1 * 0.5)
    node15 = Node(name='C', x=l2 * 2 + l1, y=0)
    node16 = Node(name='16', x=l2 + l1 * 0.5, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3)
    rod3 = Rod(start_node=node3, end_node=node4, stiffness=i3)
    rod4 = Rod(start_node=node5, end_node=node4)
    rod5 = Rod(start_node=node6, end_node=node5)
    rod6 = Rod(start_node=node7, end_node=node6)
    rod7_1 = Rod(start_node=node6, end_node=node8, stiffness=i2)
    rod7_2 = Rod(start_node=node8, end_node=node9, stiffness=i2)
    rod8_1 = Rod(start_node=node5, end_node=node16, is_start_hinge=True)
    rod8_2 = Rod(start_node=node16, end_node=node11, is_end_hinge=True)
    rod9 = Rod(start_node=node9, end_node=node10)
    rod10 = Rod(start_node=node9, end_node=node11)
    rod11 = Rod(start_node=node11, end_node=node12)
    rod12 = Rod(start_node=node12, end_node=node13, stiffness=i3)
    rod13 = Rod(start_node=node14, end_node=node13)
    rod14 = Rod(start_node=node15, end_node=node14)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node8, number_of_reactions=1, rotation=90)
    support3 = Support(node=node15, number_of_reactions=3, rotation=90)

    if load_index == 1:
        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_P2 = Force(name='P', node=node7, value=P, rotation=270)
        load_P3 = Force(name='P', node=node14, value=P, rotation=180)
        load_P4 = Force(name='P', node=node10, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod12, value=q, rotation=270)
        loads = [load_P1, load_P2, load_P3, load_P4, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15, node16]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7_1, rod7_2, rod8_1, rod8_2, rod9, rod10, rod11, rod12, rod13, rod14]

    else:
        load_P1 = Force(name='P', node=node4, value=P, rotation=180)
        load_P2 = Force(name='P', node=node12, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod2, value=q, rotation=0)
        load_q3 = DistributedForce(name='q', rod=rod13, value=q, rotation=180)
        load_q4 = DistributedForce(name='q', rod=rod14, value=q, rotation=180)
        loads = [load_P1, load_P2, load_q1, load_q2, load_q3, load_q4]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15, node16]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7_1, rod7_2, rod8_1, rod8_2, rod9, rod10, rod11, rod12, rod13, rod14]

    supports = [support1, support2, support3]

    symmetry = ('x', node8)
    details = dict()
    details['node_name_for_static_check'] = 'D'

    return nodes, rods, supports, loads, symmetry, details


def create_primary_system_18(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    details = dict()

    node8 = Node(name='B', x=l2 + l1 * 0.5, y=h1 * 0.5)
    node9 = Node(name='9', x=l2 + l1, y=h1 * 0.5)
    node10 = Node(name='10', x=l2 * 1.3 + l1, y=h1 * 0.5)
    node11 = Node(name='V', x=l2 + l1, y=h1)
    node12 = Node(name='12', x=l2 + l1, y=h1 + h2)
    node13 = Node(name='S', x=l2 * 2 + l1, y=h1, is_hinge=True)
    node14 = Node(name='K', x=l2 * 2 + l1, y=h1 * 0.5)
    node15 = Node(name='C', x=l2 * 2 + l1, y=0)

    rod7_2 = Rod(start_node=node8, end_node=node9, stiffness=i2)
    rod9 = Rod(start_node=node9, end_node=node10)
    rod10 = Rod(start_node=node9, end_node=node11)
    rod11 = Rod(start_node=node11, end_node=node12)
    rod12 = Rod(start_node=node12, end_node=node13, stiffness=i3)
    rod13 = Rod(start_node=node14, end_node=node13)
    rod14 = Rod(start_node=node15, end_node=node14)

    support1 = Support(node=node8, number_of_reactions=1, rotation=90)
    support2 = Support(node=node15, number_of_reactions=3, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node11, value=1, rotation=0)
    load_x2 = Force(name='x2', node=node8, value=1, rotation=0)
    load_x3 = Momentum(name='x3', node=node8, value=1, rotation=False)
    load_k = Force(name='x', node=node14, value=1, rotation=180)

    if load_index == 1:
        load_P3 = Force(name='P', node=node14, value=P, rotation=180)
        load_P4 = Force(name='P', node=node10, value=P, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod12, value=q, rotation=270)
        loads_p = [load_P3, load_P4, load_q2]
        nodes = [node8, node9, node10, node11, node12, node13, node14, node15]
        rods = [rod7_2, rod9, rod10, rod11, rod12, rod13, rod14]

    else:
        load_P2 = Force(name='P', node=node12, value=P, rotation=0)
        load_q3 = DistributedForce(name='q', rod=rod13, value=q, rotation=180)
        load_q4 = DistributedForce(name='q', rod=rod14, value=q, rotation=180)
        loads_p = [load_P2, load_q3, load_q4]
        nodes = [node8, node9, node10, node11, node12, node13, node14, node15]
        rods = [rod7_2, rod9, rod10, rod11, rod12, rod13, rod14]

    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2]

    details['equation_of_static_determinacy'] = ' 3 · 3 - 6 = 3'

    return nodes, rods, supports, loads, details


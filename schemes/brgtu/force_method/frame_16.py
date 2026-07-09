from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.solver import SolvableFrame
from core.mechanics.support import Support


def create_frame_16(params: dict):
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
    node3 = Node(name='3', x=0, y=h1 + h2 * 0.5)
    node4 = Node(name='L', x=l2, y=h1 + h2, is_hinge=True)
    node5 = Node(name='5', x=l2, y=h1)
    node6 = Node(name='K', x=l2 + l1 * 0.15, y=h1)
    node7 = Node(name='S', x=l2 + l1 * 0.3, y=h1, is_hinge=True)
    node8 = Node(name='B', x=l2, y=0)
    node9 = Node(name='C', x=l2 + l1 * 0.3, y=0)
    node10 = Node(name='D', x=l2 + l1 * 0.7, y=0)
    node11 = Node(name='O', x=l2 + l1 * 0.7, y=h1, is_hinge=True)
    node12 = Node(name='12', x=l2 + l1 * 0.85, y=h1)
    node13 = Node(name='13', x=l2 + l1, y=h1)
    node14 = Node(name='E', x=l2 + l1, y=0)
    node15 = Node(name='V', x=l2 + l1, y=h1 + h2, is_hinge=True)
    node16 = Node(name='16', x=l2 * 2 + l1, y=h1 + h2 * 0.5)
    node17 = Node(name='17', x=l2 * 2 + l1, y=h1 * 0.5)
    node18 = Node(name='T', x=l2 * 2 + l1, y=0)
    node19 = Node(name='19', x=l2 + l1 * 0.5, y=h1 + h2)

    rod2 = Rod(start_node=node3, end_node=node4, stiffness=i3)
    rod3 = Rod(start_node=node5, end_node=node4)
    rod4 = Rod(start_node=node8, end_node=node5)
    rod5 = Rod(start_node=node5, end_node=node6, stiffness=i2)
    rod6 = Rod(start_node=node6, end_node=node7, stiffness=i2)
    rod7 = Rod(start_node=node9, end_node=node7)
    rod8_1 = Rod(start_node=node4, end_node=node19)
    rod8_2 = Rod(start_node=node19, end_node=node15)
    rod9 = Rod(start_node=node10, end_node=node11)
    rod10 = Rod(start_node=node11, end_node=node12, stiffness=i2)
    rod11 = Rod(start_node=node12, end_node=node13, stiffness=i2)
    rod12 = Rod(start_node=node14, end_node=node13)
    rod13 = Rod(start_node=node13, end_node=node15)
    rod14 = Rod(start_node=node15, end_node=node16, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node8, number_of_reactions=2, rotation=90)
    support3 = Support(node=node9, number_of_reactions=2, rotation=90)
    support4 = Support(node=node10, number_of_reactions=2, rotation=90)
    support5 = Support(node=node14, number_of_reactions=2, rotation=90)
    support6 = Support(node=node18, number_of_reactions=3, rotation=90)

    if load_index == 1:
        rod1 = Rod(start_node=node1, end_node=node3)
        rod15 = Rod(start_node=node18, end_node=node16)

        load_P1 = Force(name='P', node=node6, value=P, rotation=270)
        load_P2 = Force(name='P', node=node12, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod14, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15, node16, node18, node19]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8_1, rod8_2, rod9, rod10, rod11, rod12, rod13, rod14, rod15]

    else:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)
        rod15_1 = Rod(start_node=node18, end_node=node17)
        rod15_2 = Rod(start_node=node17, end_node=node16)

        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_P2 = Force(name='P', node=node17, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=180)
        load_q2 = DistributedForce(name='q', rod=rod13, value=q, rotation=0)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15, node16, node17, node18, node19]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7, rod8_1, rod8_2, rod9, rod10, rod11, rod12, rod13, rod14, rod15_1, rod15_2]

    supports = [support1, support2, support3, support4, support5, support6]

    symmetry = ('x', node19)
    details = dict()
    details['node_name_for_static_check'] = 'S'

    return nodes, rods, supports, loads, symmetry, details


def create_primary_system_16(params: dict):
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

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='2', x=0, y=h1 * 0.5)
    node3 = Node(name='3', x=0, y=h1 + h2 * 0.5)
    node4 = Node(name='L', x=l2, y=h1 + h2, is_hinge=True)
    node5 = Node(name='5', x=l2, y=h1)
    node6 = Node(name='K', x=l2 + l1 * 0.15, y=h1)
    node7 = Node(name='S', x=l2 + l1 * 0.3, y=h1, is_hinge=True)
    node8 = Node(name='B', x=l2, y=0)
    node9 = Node(name='C', x=l2 + l1 * 0.3, y=0)

    rod2 = Rod(start_node=node3, end_node=node4, stiffness=i3)
    rod3 = Rod(start_node=node5, end_node=node4)
    rod4 = Rod(start_node=node8, end_node=node5)
    rod5 = Rod(start_node=node5, end_node=node6, stiffness=i2)
    rod6 = Rod(start_node=node6, end_node=node7, stiffness=i2)
    rod7 = Rod(start_node=node9, end_node=node7)

    support1 = Support(node=node1, number_of_reactions=1, rotation=90)
    support2 = Support(node=node8, number_of_reactions=2, rotation=90)
    support3 = Support(node=node9, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node4, value=1, rotation=0)
    load_x2 = Force(name='x2', node=node1, value=1, rotation=0)
    load_x3 = Momentum(name='x3', node=node1, value=1, rotation=False)
    load_k = Force(name='x', node=node6, value=1, rotation=270)

    if load_index == 1:
        rod1 = Rod(start_node=node1, end_node=node3)

        load_P1 = Force(name='P', node=node6, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
        loads_p = [load_P1, load_q1]
        nodes = [node1, node3, node4, node5, node6, node7, node8, node9]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]

        details['splitted_frames_order'] = (
            ['A', '3', 'L1'],
            ['B', '5', 'L', 'K', 'S', 'C'],
        )

    else:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)

        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=180)
        loads_p = [load_P1, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7]

        details['splitted_frames_order'] = (
            ['A', '2', '3', 'L1'],
            ['B', '5', 'L', 'K', 'S', 'C'],
        )

    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2, support3]

    details['equation_of_static_determinacy'] = ' 3 · 5 - 10 = 5'

    return nodes, rods, supports, loads, details


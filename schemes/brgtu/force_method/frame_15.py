from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.support import Support


def create_frame_15(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=l2 * 0.2, y=0)
    node2 = Node(name='2', x=l2 * 0.2, y=h1)
    node3 = Node(name='3', x=0, y=h1)
    node4 = Node(name='4', x=0, y=h1 * 0.5)
    node5 = Node(name='E', x=l2 * 0.2, y=h1 + h2)
    node6 = Node(name='D', x=l2 * 0.2 + l1, y=h1, is_hinge=True)
    node7 = Node(name='B', x=l2 * 0.2 + l1, y=0)
    node8 = Node(name='C', x=l2 * 0.8 + l1, y=0)
    node9 = Node(name='K', x=l2 * 0.8 + l1, y=h1 * 0.5)
    node10 = Node(name='10', x=l2 * 0.8 + l1, y=h1)
    node11 = Node(name='11', x=l2 + l1, y=h1)
    node12 = Node(name='12', x=l2 * 0.8 + l1, y=h1 + h2 * 0.5)
    node13 = Node(name='T', x=l2 * 0.8 + l1, y=h1 + h2)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node3, end_node=node2)
    rod3 = Rod(start_node=node4, end_node=node3)
    rod4 = Rod(start_node=node2, end_node=node6, stiffness=i2)
    rod5 = Rod(start_node=node2, end_node=node5)
    rod6 = Rod(start_node=node5, end_node=node13, is_start_hinge=True, is_end_hinge=True)
    rod7 = Rod(start_node=node7, end_node=node6)
    rod8 = Rod(start_node=node6, end_node=node10, stiffness=i3)
    rod9 = Rod(start_node=node8, end_node=node9)
    rod10 = Rod(start_node=node9, end_node=node10)
    rod11 = Rod(start_node=node10, end_node=node11)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=2, rotation=90)
    support3 = Support(node=node8, number_of_reactions=2, rotation=90)
    support4 = Support(node=node13, number_of_reactions=1, rotation=180)

    if load_index == 1:
        rod12_1 = Rod(start_node=node10, end_node=node12)
        rod12_2 = Rod(start_node=node12, end_node=node13)

        load_P1 = Force(name='P', node=node9, value=P, rotation=180)
        load_P2 = Force(name='P', node=node12, value=P / 2, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod11, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12_1, rod12_2]

    else:
        rod12 = Rod(start_node=node10, end_node=node13)

        load_P1 = Force(name='P', node=node4, value=P, rotation=180)
        load_P2 = Force(name='P', node=node9, value=P / 2, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod5, value=q, rotation=0)
        loads = [load_P1, load_P2, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node13]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12]

    supports = [support1, support2, support3, support4]

    symmetry = None
    details = dict()
    details['node_name_for_static_check'] = 'D'

    return nodes, rods, supports, loads, symmetry, details


def create_primary_system_15(params: dict):
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

    node1 = Node(name='A', x=l2 * 0.2, y=0)
    node2 = Node(name='2', x=l2 * 0.2, y=h1)
    node3 = Node(name='3', x=0, y=h1)
    node4 = Node(name='4', x=0, y=h1 * 0.5)
    node5 = Node(name='E', x=l2 * 0.2, y=h1 + h2)
    node6 = Node(name='D', x=l2 * 0.2 + l1, y=h1, is_hinge=True)
    node7 = Node(name='B', x=l2 * 0.2 + l1, y=0)
    node8 = Node(name='C', x=l2 * 0.8 + l1, y=0)
    node9 = Node(name='K', x=l2 * 0.8 + l1, y=h1 * 0.5)
    node10 = Node(name='10', x=l2 * 0.8 + l1, y=h1)
    node11 = Node(name='11', x=l2 + l1, y=h1)
    node12 = Node(name='12', x=l2 * 0.8 + l1, y=h1 + h2 * 0.5)
    node13 = Node(name='T', x=l2 * 0.8 + l1, y=h1 + h2)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node3, end_node=node2)
    rod3 = Rod(start_node=node4, end_node=node3)
    rod4 = Rod(start_node=node2, end_node=node6, stiffness=i2)
    rod5 = Rod(start_node=node2, end_node=node5)
    rod7 = Rod(start_node=node7, end_node=node6)
    rod8 = Rod(start_node=node6, end_node=node10, stiffness=i3)
    rod9 = Rod(start_node=node8, end_node=node9)
    rod10 = Rod(start_node=node9, end_node=node10)
    rod11 = Rod(start_node=node10, end_node=node11)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=2, rotation=90)
    support3 = Support(node=node13, number_of_reactions=1, rotation=180)

    loads = {}
    load_x1_1 = Force(name='x1', node=node5, value=1, rotation=0)
    load_x1_2 = Force(name='x1', node=node13, value=1, rotation=180)
    load_x2 = Force(name='x2', node=node8, value=1, rotation=90)
    load_x3 = Force(name='x3', node=node8, value=1, rotation=180)
    load_k = Force(name='x', node=node9, value=1, rotation=0)

    if load_index == 1:
        rod12_1 = Rod(start_node=node10, end_node=node12)
        rod12_2 = Rod(start_node=node12, end_node=node13)

        load_P1 = Force(name='P', node=node9, value=P, rotation=180)
        load_P2 = Force(name='P', node=node12, value=P / 2, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod11, value=q, rotation=270)
        loads_p = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
        rods = [rod1, rod2, rod3, rod4, rod5, rod7, rod8, rod9, rod10, rod11, rod12_1, rod12_2]

        details['splitted_frames_order'] = (
            ['D1', '10', '11', 'K', 'C', '12', 'T'],
            ['A', 'B', 'D', '2', '3', '4', 'E'],
        )

    else:
        rod12 = Rod(start_node=node10, end_node=node13)

        load_P1 = Force(name='P', node=node4, value=P, rotation=180)
        load_P2 = Force(name='P', node=node9, value=P / 2, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod5, value=q, rotation=0)
        loads_p = [load_P1, load_P2, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node13]
        rods = [rod1, rod2, rod3, rod4, rod5, rod7, rod8, rod9, rod10, rod11, rod12]

        details['splitted_frames_order'] = (
            ['D1', '10', '11', 'K', 'C', 'T'],
            ['A', 'B', 'D', '2', '3', '4', 'E'],
        )


    loads['1'] = [load_x1_1, load_x1_2]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2, support3]

    details['equation_of_static_determinacy'] = ' 3 · 4 - 9 = 3'

    return nodes, rods, supports, loads, details

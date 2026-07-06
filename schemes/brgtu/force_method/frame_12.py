from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.support import Support


def create_frame_12(params: dict):
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
    node3 = Node(name='S', x=0, y=h1, is_hinge=True)
    node4 = Node(name='4', x=l1 * 0.5, y=h1)
    node5 = Node(name='K', x=l1 * 0.5, y=h1 * 0.5)
    node6 = Node(name='B', x=l1 * 0.5, y=0)
    node7 = Node(name='O', x=l1 * 0.5 + l2, y=h1 + h2 * 0.5, is_hinge=True)
    node8 = Node(name='V', x=l1 * 0.5 + l2, y=h1 * 0.8)
    node9 = Node(name='C', x=l1 * 0.5 + l2, y=0)
    node10 = Node(name='D', x=l1 * 1.5 + l2, y=0)
    node11 = Node(name='G', x=l1 * 1.5 + l2, y=h1 * 0.8)
    node12 = Node(name='L', x=l1 * 1.5 + l2, y=h1 + h2 * 0.5, is_hinge=True)
    node13 = Node(name='13', x=l1 * 1.5 + l2 * 2, y=h1)
    node14 = Node(name='14', x=l1 * 1.5 + l2 * 2, y=h1 * 0.5)
    node15 = Node(name='E', x=l1 * 1.5 + l2 * 2, y=0)
    node16 = Node(name='W', x=l1 * 2 + l2 * 2, y=h1, is_hinge=True)
    node17 = Node(name='17', x=l1 * 2 + l2 * 2, y=h1 * 0.5)
    node18 = Node(name='T', x=l1 * 2 + l2 * 2, y=0)
    node19 = Node(name='19', x=l1 + l2, y=h1 * 0.8)

    rod2 = Rod(start_node=node3, end_node=node4, stiffness=i2)
    rod3 = Rod(start_node=node6, end_node=node5)
    rod4 = Rod(start_node=node5, end_node=node4)
    rod5 = Rod(start_node=node4, end_node=node7, stiffness=i3)
    rod6 = Rod(start_node=node8, end_node=node7)
    rod7 = Rod(start_node=node9, end_node=node8)
    rod8_1 = Rod(start_node=node8, end_node=node19, is_start_hinge=True)
    rod8_2 = Rod(start_node=node19, end_node=node11, is_end_hinge=True)
    rod9 = Rod(start_node=node10, end_node=node11)
    rod10 = Rod(start_node=node11, end_node=node12)
    rod11 = Rod(start_node=node12, end_node=node13, stiffness=i3)
    rod12 = Rod(start_node=node14, end_node=node13)
    rod13 = Rod(start_node=node15, end_node=node14)
    rod14 = Rod(start_node=node13, end_node=node16, stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node6, number_of_reactions=2, rotation=90)
    support3 = Support(node=node9, number_of_reactions=2, rotation=90)
    support4 = Support(node=node10, number_of_reactions=2, rotation=90)
    support5 = Support(node=node15, number_of_reactions=2, rotation=90)
    support6 = Support(node=node18, number_of_reactions=3, rotation=90)

    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)
        rod15_1 = Rod(start_node=node18, end_node=node17)
        rod15_2 = Rod(start_node=node17, end_node=node16)

        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_P2 = Force(name='P', node=node17, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod5, value=q, rotation=270)
        load_q3 = DistributedForce(name='q', rod=rod11, value=q, rotation=270)
        load_q4 = DistributedForce(name='q', rod=rod14, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2, load_q3, load_q4]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14,
                 node15, node16, node17, node18, node19]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7, rod8_1, rod8_2, rod9, rod10, rod11, rod12, rod13,
                rod14, rod15_1, rod15_2]

    else:
        rod1 = Rod(start_node=node1, end_node=node3)
        rod15 = Rod(start_node=node18, end_node=node16)

        load_P1 = Force(name='P', node=node5, value=P, rotation=0)
        load_P2 = Force(name='P', node=node7, value=P, rotation=180)
        load_P3 = Force(name='P', node=node12, value=P, rotation=0)
        load_P4 = Force(name='P', node=node14, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod15, value=q, rotation=180)
        loads = [load_P1, load_P2, load_P3, load_P4, load_q1, load_q2]
        nodes = [node1, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14,
                 node15, node16, node18, node19]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8_1, rod8_2, rod9, rod10, rod11, rod12, rod13,
                rod14, rod15]

    supports = [support1, support2, support3, support4, support5, support6]

    symmetry = ('x', node19)
    details = dict()
    details['node_name_for_static_check'] = 'O'

    return nodes, rods, supports, loads, symmetry, details


def create_primary_system_12(params: dict):
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
    node3 = Node(name='S', x=0, y=h1, is_hinge=True)
    node4 = Node(name='4', x=l1 * 0.5, y=h1)
    node5 = Node(name='K', x=l1 * 0.5, y=h1 * 0.5)
    node6 = Node(name='B', x=l1 * 0.5, y=0)
    node7 = Node(name='O', x=l1 * 0.5 + l2, y=h1 + h2 * 0.5, is_hinge=True)
    node8 = Node(name='V', x=l1 * 0.5 + l2, y=h1 * 0.8)
    node9 = Node(name='C', x=l1 * 0.5 + l2, y=0)

    rod2 = Rod(start_node=node3, end_node=node4, stiffness=i2)
    rod3 = Rod(start_node=node6, end_node=node5)
    rod4 = Rod(start_node=node5, end_node=node4)
    rod5 = Rod(start_node=node4, end_node=node7, stiffness=i3)
    rod6 = Rod(start_node=node8, end_node=node7)
    rod7 = Rod(start_node=node9, end_node=node8)

    support1 = Support(node=node1, number_of_reactions=1, rotation=0)
    support2 = Support(node=node6, number_of_reactions=2, rotation=90)
    support3 = Support(node=node9, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node8, value=1, rotation=0)
    load_x2 = Force(name='x2', node=node1, value=1, rotation=90)
    load_x3 = Momentum(name='x3', node=node1, value=1, rotation=False)
    load_k = Force(name='x', node=node5, value=1, rotation=0)

    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)

        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod5, value=q, rotation=270)
        loads_p = [load_P1, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7]

        details['splitted_frames_order'] = (
            ['A', '2', 'S1'],
            ['S', 'B', 'K', '4', 'O', 'V', 'C'],
        )

    else:
        rod1 = Rod(start_node=node1, end_node=node3)

        load_P1 = Force(name='P', node=node5, value=P, rotation=0)
        load_P2 = Force(name='P', node=node7, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        loads_p = [load_P1, load_P2, load_q1]
        nodes = [node1, node3, node4, node5, node6, node7, node8, node9]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]

        details['splitted_frames_order'] = (
            ['A', 'S1'],
            ['S', 'B', 'K', '4', 'O', 'V', 'C'],
        )


    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2, support3]

    details['equation_of_static_determinacy'] = ' 3 · 5 - 10 = 5'

    return nodes, rods, supports, loads, details

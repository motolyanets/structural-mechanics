from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.support import Support


def create_frame_13(params: dict):
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
    node2 = Node(name='2', x=l1 * 0.5, y=h1)
    node3 = Node(name='B', x=l1 * 0.5, y=0)
    node4 = Node(name='E', x=l1 * 0.5, y=h1 + h2, is_hinge=True)
    node5 = Node(name='T', x=l1 * 0.5 + l2, y=h1 + h2)
    node6 = Node(name='K', x=l1 * 0.5 + l2, y=h1)
    node7 = Node(name='C', x=l1 * 0.5 + l2, y=0)
    node8 = Node(name='V', x=l1 * 1.5 + l2, y=h1 + h2, is_hinge=True)
    node9 = Node(name='9', x=l1 * 1.5 + l2, y=h1)
    node10 = Node(name='D', x=l1 * 1.5 + l2, y=0)
    node11 = Node(name='11', x=l1 * 0.5 + l2 * 0.5, y=h1 + h2)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod2 = Rod(start_node=node3, end_node=node2)
    rod3 = Rod(start_node=node2, end_node=node4)
    rod5 = Rod(start_node=node6, end_node=node5)
    rod6 = Rod(start_node=node7, end_node=node6)
    rod7 = Rod(start_node=node5, end_node=node8, is_start_hinge=True)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node3, number_of_reactions=2, rotation=90)
    support3 = Support(node=node7, number_of_reactions=2, rotation=90)
    support4 = Support(node=node10, number_of_reactions=3, rotation=90)

    if load_index == 1:
        rod4_1 = Rod(start_node=node4, end_node=node11, stiffness=i3)
        rod4_2 = Rod(start_node=node11, end_node=node5, stiffness=i3)
        rod8 = Rod(start_node=node10, end_node=node8)

        load_P1 = Force(name='P', node=node11, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod8, value=q, rotation=180)
        loads = [load_P1, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node10, node11]
        rods = [rod1, rod2, rod3, rod4_1, rod4_2, rod5, rod6, rod7, rod8]

    else:
        rod4 = Rod(start_node=node4, end_node=node5, stiffness=i3)
        rod8_1 = Rod(start_node=node10, end_node=node9)
        rod8_2 = Rod(start_node=node9, end_node=node8)

        load_P1 = Force(name='P', node=node6, value=P, rotation=0)
        load_P2 = Force(name='P', node=node9, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=0)
        loads = [load_P1, load_P2, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8_1, rod8_2]

    supports = [support1, support2, support3, support4]

    symmetry = None
    details = dict()
    details['node_name_for_static_check'] = 'E'

    return nodes, rods, supports, loads, symmetry, details


def create_primary_system_13(params: dict):
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
    node2 = Node(name='2', x=l1 * 0.5, y=h1)
    node3 = Node(name='B', x=l1 * 0.5, y=0)
    node4 = Node(name='E', x=l1 * 0.5, y=h1 + h2, is_hinge=True)
    node5 = Node(name='T', x=l1 * 0.5 + l2, y=h1 + h2)
    node6 = Node(name='K', x=l1 * 0.5 + l2, y=h1)
    node7 = Node(name='C', x=l1 * 0.5 + l2, y=0)
    node8 = Node(name='V', x=l1 * 1.5 + l2, y=h1 + h2)
    node9 = Node(name='9', x=l1 * 1.5 + l2, y=h1)
    node10 = Node(name='D', x=l1 * 1.5 + l2, y=0)
    node11 = Node(name='11', x=l1 * 0.5 + l2 * 0.5, y=h1 + h2)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod2 = Rod(start_node=node3, end_node=node2)
    rod3 = Rod(start_node=node2, end_node=node4)
    rod5 = Rod(start_node=node6, end_node=node5)
    rod6 = Rod(start_node=node7, end_node=node6)

    support1 = Support(node=node3, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=2, rotation=90)
    support3 = Support(node=node10, number_of_reactions=3, rotation=90)

    loads = {}
    load_x1_1 = Force(name='x1', node=node5, value=1, rotation=0)
    load_x1_2 = Force(name='x1', node=node8, value=1, rotation=180)
    load_x2 = Force(name='x2', node=node1, value=1, rotation=90)
    load_x3 = Force(name='x3', node=node1, value=1, rotation=180)
    load_k = Force(name='x', node=node5, value=1, rotation=0)

    if load_index == 1:
        rod4_1 = Rod(start_node=node4, end_node=node11, stiffness=i3)
        rod4_2 = Rod(start_node=node11, end_node=node5, stiffness=i3)
        rod8 = Rod(start_node=node10, end_node=node8)

        load_P1 = Force(name='P', node=node11, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod8, value=q, rotation=180)
        loads_p = [load_P1, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node10, node11]
        rods = [rod1, rod2, rod3, rod4_1, rod4_2, rod5, rod6, rod8]

        details['splitted_frames_order'] = (
            ['D', 'V'],
            ['A', 'B', '2', 'E', '11', 'T', 'K', 'C'],
        )

    else:
        rod4 = Rod(start_node=node4, end_node=node5, stiffness=i3)
        rod8_1 = Rod(start_node=node10, end_node=node9)
        rod8_2 = Rod(start_node=node9, end_node=node8)

        load_P1 = Force(name='P', node=node6, value=P, rotation=0)
        load_P2 = Force(name='P', node=node9, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=0)
        loads_p = [load_P1, load_P2, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod8_1, rod8_2]

        details['splitted_frames_order'] = (
            ['D', '9', 'V'],
            ['A', 'B', '2', 'E', 'T', 'K', 'C'],
        )


    loads['1'] = [load_x1_1, load_x1_2]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2, support3]

    details['equation_of_static_determinacy'] = ' 3 · 3 - 6 = 3'

    return nodes, rods, supports, loads, details

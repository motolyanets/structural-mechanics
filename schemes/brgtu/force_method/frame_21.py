from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, DistributedForce, Momentum
from core.mechanics.support import Support


def create_frame_21(params: dict):
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
    node3 = Node(name='3', x=0, y=h1)
    node4 = Node(name='4', x=l2, y=h1 + h2)
    node5 = Node(name='E', x=l2, y=h1 * 0.5, is_hinge=True)
    node6 = Node(name='B', x=l2, y=0)
    node7 = Node(name='7', x=l2, y=h1 + h2 * 1.5)
    node8 = Node(name='8', x=l2 + l1 * 0.5, y=h1 + h2 * 1.5)
    node9 = Node(name='9', x=l2 + l1, y=h1 + h2 * 1.5)
    node10 = Node(name='10', x=l2 + l1, y=h1 + h2)
    node11 = Node(name='11', x=l1 + l2* 2, y=h1)
    node12 = Node(name='T', x=l1 + l2, y=h1 * 0.5, is_hinge=True)
    node13 = Node(name='C', x=l1 + l2, y=0)
    node14 = Node(name='D', x=l1 + l2 * 2, y=0)
    node15 = Node(name='15', x=l1 + l2 * 2, y=h1 * 0.5)

    rod1_1 = Rod(start_node=node1, end_node=node2)
    rod1_2 = Rod(start_node=node2, end_node=node3)
    rod2 = Rod(start_node=node3, end_node=node4, stiffness=i2)
    rod3 = Rod(start_node=node6, end_node=node5)
    rod4 = Rod(start_node=node5, end_node=node4)
    rod5 = Rod(start_node=node4, end_node=node7)
    rod6 = Rod(start_node=node7, end_node=node8, stiffness=i3)
    # rod7 = Rod(start_node=node5, end_node=node12)
    rod8 = Rod(start_node=node8, end_node=node9, stiffness=i3)
    rod9 = Rod(start_node=node10, end_node=node9)
    rod10 = Rod(start_node=node12, end_node=node10)
    rod11 = Rod(start_node=node13, end_node=node12)
    rod12 = Rod(start_node=node10, end_node=node11, stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node6, number_of_reactions=2, rotation=90)
    support3 = Support(node=node13, number_of_reactions=2, rotation=90)
    support4 = Support(node=node14, number_of_reactions=2, rotation=90)

    if load_index == 1:
        # rod13 = Rod(start_node=node14, end_node=node11)
        rod13_1 = Rod(start_node=node14, end_node=node15)
        rod13_2 = Rod(start_node=node15, end_node=node11)


        load_P1 = Force(name='P', node=node8, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod12, value=q, rotation=270)
        loads = [load_P1, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15]
        # rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12, rod13_1, rod13_2]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod8, rod9, rod10, rod11, rod12, rod13_1, rod13_2]

    else:
        rod13_1 = Rod(start_node=node14, end_node=node15)
        rod13_2 = Rod(start_node=node15, end_node=node11)

        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_P2 = Force(name='P', node=node15, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod8, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15]
        # rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12, rod13_1, rod13_2]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod8, rod9, rod10, rod11, rod12, rod13_1, rod13_2]

    supports = [support1, support2, support3, support4]

    symmetry = ('x', node8)
    details = dict()
    details['node_name_for_static_check'] = 'E'

    return nodes, rods, supports, loads, symmetry, details


def create_primary_system_21(params: dict):
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
    node3 = Node(name='3', x=0, y=h1)
    node4 = Node(name='4', x=l2, y=h1 + h2)
    node5 = Node(name='E', x=l2, y=h1 * 0.5, is_hinge=True)
    node6 = Node(name='B', x=l2, y=0)
    node7 = Node(name='7', x=l2, y=h1 + h2 * 1.5)
    node8 = Node(name='8', x=l2 + l1 * 0.5, y=h1 + h2 * 1.5)

    rod1_1 = Rod(start_node=node1, end_node=node2)
    rod1_2 = Rod(start_node=node2, end_node=node3)
    rod2 = Rod(start_node=node3, end_node=node4, stiffness=i2)
    rod3 = Rod(start_node=node6, end_node=node5)
    rod4 = Rod(start_node=node5, end_node=node4)
    rod5 = Rod(start_node=node4, end_node=node7)
    rod6 = Rod(start_node=node7, end_node=node8, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node6, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node5, value=1, rotation=0)
    load_x2 = Force(name='x2', node=node8, value=1, rotation=0)
    load_x3 = Momentum(name='x3', node=node8, value=1, rotation=True)
    load_k = Force(name='x', node=node2, value=1, rotation=0)

    if load_index == 1:
        load_P1 = Force(name='P', node=node8, value=P / 2, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
        loads_p = [load_P1, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6]

    else:
        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        loads_p = [load_P1, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6]

    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2]

    details = dict()
    details['equation_of_static_determinacy'] = ' 3 · 4 - 8 = 4'

    return nodes, rods, supports, loads, details


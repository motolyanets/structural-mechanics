from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.support import Support


def create_frame_26(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=h1)
    node2 = Node(name='2', x=l2, y=h1 + h2 * 0.5)
    node3 = Node(name='K', x=l2, y=h1)
    node4 = Node(name='E', x=l2, y=h1 / 2, is_hinge=True)
    node5 = Node(name='B', x=l2, y=0)
    node6 = Node(name='6', x=l2, y=h1 + h2)
    node7 = Node(name='7', x=l2 + l1 / 2, y=h1 + h2)
    node8 = Node(name='8', x=l2 + l1, y=h1 + h2)
    node9 = Node(name='9', x=l2 + l1, y=h1 + h2 * 0.5)
    node10 = Node(name='10', x=l2 + l1, y=h1)
    node11 = Node(name='T', x=l2 + l1, y=h1 / 2, is_hinge=True)
    node12 = Node(name='C', x=l2 + l1, y=0)
    node13 = Node(name='D', x=l2 * 2 + l1, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod2 = Rod(start_node=node3, end_node=node2)
    rod3 = Rod(start_node=node4, end_node=node3)
    rod4 = Rod(start_node=node5, end_node=node4)
    rod5 = Rod(start_node=node2, end_node=node6)
    rod6 = Rod(start_node=node6, end_node=node7, stiffness=i3)
    rod7 = Rod(start_node=node7, end_node=node8, stiffness=i3)
    rod8 = Rod(start_node=node9, end_node=node8)
    rod9 = Rod(start_node=node10, end_node=node9)
    rod10 = Rod(start_node=node11, end_node=node10)
    rod11 = Rod(start_node=node12, end_node=node11)
    rod12 = Rod(start_node=node9, end_node=node13, stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node5, number_of_reactions=3, rotation=90)
    support3 = Support(node=node12, number_of_reactions=3, rotation=90)
    support4 = Support(node=node13, number_of_reactions=2, rotation=90)

    if load_index == 1:
        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_P2 = Force(name='P', node=node10, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod7, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12]

    else:
        load_P1 = Force(name='P', node=node7, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod12, value=q, rotation=270)
        loads = [load_P1, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12]

    supports = [support1, support2, support3, support4]

    symmetry = ('x', node7)
    details = dict()
    details['node_name_for_static_check'] = 'E'

    return nodes, rods, supports, loads, symmetry, details


def create_primary_system_26(params: dict):
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

    node1 = Node(name='A', x=0, y=h1)
    node2 = Node(name='2', x=l2, y=h1 + h2 * 0.5)
    node3 = Node(name='K', x=l2, y=h1)
    node4 = Node(name='E', x=l2, y=h1 / 2, is_hinge=True)
    node5 = Node(name='B', x=l2, y=0)
    node6 = Node(name='6', x=l2, y=h1 + h2)
    node7 = Node(name='7', x=l2 + l1 / 2, y=h1 + h2)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod2 = Rod(start_node=node3, end_node=node2)
    rod3 = Rod(start_node=node4, end_node=node3)
    rod4 = Rod(start_node=node5, end_node=node4)
    rod5 = Rod(start_node=node2, end_node=node6)
    rod6 = Rod(start_node=node6, end_node=node7, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=1, rotation=90)
    support2 = Support(node=node5, number_of_reactions=3, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node1, value=1, rotation=0)
    load_x2 = Force(name='x2', node=node7, value=1, rotation=0)
    load_x3 = Momentum(name='x3', node=node7, value=1, rotation=False)
    load_k = Force(name='x', node=node3, value=1, rotation=0)

    if load_index == 1:
        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        loads_p = [load_P1, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6]

    else:
        load_P1 = Force(name='P', node=node7, value=P / 2, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        loads_p = [load_P1, load_q1]
        nodes = [node1, node2, node3, node4, node5, node6, node7]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6]

    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2]

    details['equation_of_static_determinacy'] = ' 3 · 5 - 10 = 5'

    return nodes, rods, supports, loads, details


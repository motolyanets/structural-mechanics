from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, DistributedForce, Momentum
from core.mechanics.support import Support


def create_frame_19(params: dict):
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
    node2 = Node(name='2', x=l1 / 3, y=0)
    node3 = Node(name='3', x=l1 / 3, y=h1 * 0.5)
    node4 = Node(name='C', x=l1 / 3, y=h1, is_hinge=True)
    node5 = Node(name='K', x=l1 / 3 + l2 * 0.5, y=h1)
    node6 = Node(name='6', x=l1 / 3 + l2, y=h1)
    node7 = Node(name='D', x=l1 / 3 + l2, y=h1 + h2, is_hinge=True)
    node8 = Node(name='B', x=l1 / 3 + l2, y=0)
    node9 = Node(name='9', x=l1 / 3 + l2 + l1 * 0.5, y=h1)
    node10 = Node(name='E', x=l1 / 3 + l2 + l1, y=0)
    node11 = Node(name='V', x=l1 / 3 + l2 + l1, y=h1 + h2, is_hinge=True)
    node12 = Node(name='12', x=l1 / 3 + l2 + l1, y=h1)
    node13 = Node(name='13', x=l1 / 3 + l2 * 1.5 + l1, y=h1)
    node14 = Node(name='S', x=l1 / 3 + l2 * 2 + l1, y=h1, is_hinge=True)
    node15 = Node(name='15', x=l1 / 3 + l2 * 2 + l1, y=h1 * 0.5)
    node16 = Node(name='16', x=l1 / 3 + l2 * 2 + l1, y=0)
    node17 = Node(name='T', x=l1 * 2 / 3 + l2 * 2 + l1, y=0)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod3 = Rod(start_node=node4, end_node=node5, stiffness=i3)
    rod4 = Rod(start_node=node5, end_node=node6, stiffness=i3)
    rod5 = Rod(start_node=node6, end_node=node7)
    rod6 = Rod(start_node=node8, end_node=node6)
    rod7 = Rod(start_node=node6, end_node=node9, stiffness=i3)
    rod8 = Rod(start_node=node7, end_node=node11)
    rod9 = Rod(start_node=node9, end_node=node12, stiffness=i3)
    rod10 = Rod(start_node=node12, end_node=node11)
    rod11 = Rod(start_node=node10, end_node=node12)
    rod14 = Rod(start_node=node16, end_node=node17, stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node8, number_of_reactions=2, rotation=90)
    support3 = Support(node=node10, number_of_reactions=2, rotation=90)
    support4 = Support(node=node17, number_of_reactions=2, rotation=90)

    if load_index == 1:
        rod2_1 = Rod(start_node=node2, end_node=node3)
        rod2_2 = Rod(start_node=node3, end_node=node4)
        rod13_1 = Rod(start_node=node15, end_node=node14)
        rod13_2 = Rod(start_node=node16, end_node=node15)
        rod12 = Rod(start_node=node12, end_node=node14, stiffness=i3)

        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_P2 = Force(name='P', node=node9, value=P, rotation=270)
        load_P3 = Force(name='P', node=node15, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_q3 = DistributedForce(name='q', rod=rod12, value=q, rotation=270)
        loads = [load_P1, load_P2, load_P3, load_q1, load_q2, load_q3]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node14, node15, node16, node17]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12, rod13_1, rod13_2, rod14]

    else:
        rod2 = Rod(start_node=node2, end_node=node4)
        rod13 = Rod(start_node=node16, end_node=node14)
        rod12_1 = Rod(start_node=node12, end_node=node13, stiffness=i3)
        rod12_2 = Rod(start_node=node13, end_node=node14, stiffness=i3)

        load_P1 = Force(name='P', node=node5, value=P, rotation=270)
        load_P2 = Force(name='P', node=node13, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod13, value=q, rotation=180)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node16, node17]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12_1, rod12_2, rod13, rod14]

    supports = [support1, support2, support3, support4]

    return nodes, rods, supports, loads


def create_primary_system_19(params: dict):
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
    node2 = Node(name='2', x=l1 / 3, y=0)
    node3 = Node(name='3', x=l1 / 3, y=h1 * 0.5)
    node4 = Node(name='C', x=l1 / 3, y=h1, is_hinge=True)
    node5 = Node(name='K', x=l1 / 3 + l2 * 0.5, y=h1)
    node6 = Node(name='6', x=l1 / 3 + l2, y=h1)
    node7 = Node(name='D', x=l1 / 3 + l2, y=h1 + h2)
    node8 = Node(name='B', x=l1 / 3 + l2, y=0)
    node9 = Node(name='9', x=l1 / 3 + l2 + l1 * 0.5, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod3 = Rod(start_node=node4, end_node=node5, stiffness=i3)
    rod4 = Rod(start_node=node5, end_node=node6, stiffness=i3)
    rod5 = Rod(start_node=node6, end_node=node7)
    rod6 = Rod(start_node=node8, end_node=node6)
    rod7 = Rod(start_node=node6, end_node=node9, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node8, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node7, value=1, rotation=0)
    load_x2 = Force(name='x2', node=node9, value=1, rotation=0)
    load_x3 = Momentum(name='x3', node=node9, value=1, rotation=True)
    load_k = Force(name='x', node=node5, value=1, rotation=270)

    if load_index == 1:
        rod2_1 = Rod(start_node=node2, end_node=node3)
        rod2_2 = Rod(start_node=node3, end_node=node4)

        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_P2 = Force(name='P', node=node9, value=P / 2, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        loads_p = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4, rod5, rod6, rod7]

    else:
        rod2 = Rod(start_node=node2, end_node=node4)

        load_P1 = Force(name='P', node=node5, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=0)
        loads_p = [load_P1, load_q1]
        nodes = [node1, node2, node4, node5, node6, node7, node8, node9]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]

    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2]

    return nodes, rods, supports, loads


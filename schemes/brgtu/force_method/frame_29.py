from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.solver import SolvableFrame
from core.mechanics.support import Support


def create_frame_29(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=h1 * 0.5)
    node2 = Node(name='2', x=0, y=h1 * 0.5 + h2)
    node3 = Node(name='K', x=l2 * 0.35, y=h1 * 0.5 + h2)
    node4 = Node(name='E', x=l2 * 0.7, y=h1 * 0.5 + h2, is_hinge=True)
    node5 = Node(name='5', x=l2, y=h1 * 0.5 + h2)
    node6 = Node(name='T', x=l2, y=h1 * 0.5)
    node7 = Node(name='B', x=l2, y=0)
    node8 = Node(name='C', x=l2 + l1 * 0.4, y=h2 + h1 * 0.75)
    node9 = Node(name='9', x=l2 + l1 * 0.8, y=h2 + h1)
    node10 = Node(name='10', x=l2 + l1 * 1.2, y=h2 + h1 * 0.75)
    node11 = Node(name='11', x=l2 + l1 * 1.6, y=h2 + h1 * 0.5)
    node12 = Node(name='C', x=l2 + l1 * 1.6, y=0)
    node13 = Node(name='S', x=l2 + l1 * 1.6, y=h1 * 0.5)
    node14 = Node(name='L', x=l2 * 1.3 + l1 * 1.6, y=h2 + h1 * 0.5, is_hinge=True)
    node15 = Node(name='15', x=l2 * 1.65 + l1 * 1.6, y=h2 + h1 * 0.5)
    node16 = Node(name='16', x=l2 * 2 + l1 * 1.6, y=h2 + h1 * 0.5)
    node17 = Node(name='D', x=l2 * 2 + l1 * 1.6, y=h1 * 0.5)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=i2)
    rod3 = Rod(start_node=node3, end_node=node4, stiffness=i2)
    rod4 = Rod(start_node=node4, end_node=node5, stiffness=i2)
    rod5 = Rod(start_node=node6, end_node=node5)
    rod6 = Rod(start_node=node7, end_node=node6)
    rod9 = Rod(start_node=node12, end_node=node13)
    rod10 = Rod(start_node=node13, end_node=node11)
    rod11 = Rod(start_node=node11, end_node=node14, stiffness=i2)
    rod13 = Rod(start_node=node17, end_node=node16)
    rod14 = Rod(start_node=node6, end_node=node13, is_start_hinge=True, is_end_hinge=True)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=2, rotation=90)
    support3 = Support(node=node12, number_of_reactions=2, rotation=90)
    support4 = Support(node=node17, number_of_reactions=2, rotation=90)

    if load_index == 1:
        rod7 = Rod(start_node=node5, end_node=node9, stiffness=i3)
        rod8 = Rod(start_node=node9, end_node=node11, stiffness=i3)
        rod12_1 = Rod(start_node=node14, end_node=node15, stiffness=i2)
        rod12_2 = Rod(start_node=node15, end_node=node16, stiffness=i2)
        load_P1 = Force(name='P', node=node3, value=P, rotation=270)
        load_P2 = Force(name='P', node=node15, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod7, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod8, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node9, node11, node12, node13, node14, node15, node16, node17]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12_1, rod12_2, rod13, rod14]
    else:
        rod7_1 = Rod(start_node=node5, end_node=node8, stiffness=i3)
        rod7_2 = Rod(start_node=node8, end_node=node9, stiffness=i3)
        rod8_1 = Rod(start_node=node9, end_node=node10, stiffness=i3)
        rod8_2 = Rod(start_node=node10, end_node=node11, stiffness=i3)
        rod12 = Rod(start_node=node14, end_node=node16, stiffness=i2)
        load_P1 = Force(name='P', node=node8, value=P, rotation=270)
        load_P2 = Force(name='P', node=node10, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod13, value=q, rotation=180)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node16, node17]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7_1, rod7_2, rod8_1, rod8_2, rod9, rod10, rod11, rod12, rod13, rod14]

    supports = [support1, support2, support3, support4]

    return nodes, rods, supports, loads


def create_primary_system_29(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=h1 * 0.5)
    node2 = Node(name='2', x=0, y=h1 * 0.5 + h2)
    node3 = Node(name='K', x=l2 * 0.35, y=h1 * 0.5 + h2)
    node4 = Node(name='E', x=l2 * 0.7, y=h1 * 0.5 + h2, is_hinge=True)
    node5 = Node(name='5', x=l2, y=h1 * 0.5 + h2)
    node6 = Node(name='T', x=l2, y=h1 * 0.5)
    node7 = Node(name='B', x=l2, y=0)
    node8 = Node(name='C', x=l2 + l1 * 0.4, y=h2 + h1 * 0.75)
    node9 = Node(name='9', x=l2 + l1 * 0.8, y=h2 + h1)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=i2)
    rod3 = Rod(start_node=node3, end_node=node4, stiffness=i2)
    rod4 = Rod(start_node=node4, end_node=node5, stiffness=i2)
    rod5 = Rod(start_node=node6, end_node=node5)
    rod6 = Rod(start_node=node7, end_node=node6)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node9, value=1, rotation=180)
    load_x2 = Momentum(name='x2', node=node9, value=1, rotation=False)
    load_x3 = Force(name='x3', node=node6, value=1, rotation=180)

    if load_index == 1:
        rod7 = Rod(start_node=node5, end_node=node9, stiffness=i3)
        load_P = Force(name='P', node=node3, value=P, rotation=270)
        load_q = DistributedForce(name='q', rod=rod7, value=q, rotation=270)
        loads_p = [load_P, load_q]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node9]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]
    else:
        rod7_1 = Rod(start_node=node5, end_node=node8, stiffness=i3)
        rod7_2 = Rod(start_node=node8, end_node=node9, stiffness=i3)
        load_P = Force(name='P', node=node8, value=P, rotation=270)
        load_q = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        loads_p = [load_P, load_q]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7_1, rod7_2]

    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    supports = [support1, support2]

    return nodes, rods, supports, loads


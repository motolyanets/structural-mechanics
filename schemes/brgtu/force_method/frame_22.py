from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.solver import SolvableFrame
from core.mechanics.support import Support


def create_frame_22(params: dict):
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
    node2 = Node(name='2', x=0, y=h1)
    node3 = Node(name='3', x=l1 * 0.5, y=h1 + h2 * 0.75)
    node4 = Node(name='4', x=l1, y=h1 + h2 * 1.5)
    node5 = Node(name='K', x=l1 + l2 * 0.5, y=h1 + h2 * 1.5)
    node6 = Node(name='C', x=l1 + l2, y=h1 + h2 * 1.5, is_hinge=True)
    node7 = Node(name='D', x=l1, y=h1, is_hinge=True)
    node8 = Node(name='8', x=l1 + l2, y=h1)
    node9 = Node(name='9', x=l1 * 1.3 + l2, y=h1)
    node10 = Node(name='B', x=l1 + l2, y=0)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod3 = Rod(start_node=node4, end_node=node5, stiffness=i3)
    rod4 = Rod(start_node=node5, end_node=node6, stiffness=i3)
    rod5 = Rod(start_node=node2, end_node=node7, stiffness=i2)
    rod6 = Rod(start_node=node7, end_node=node8, stiffness=i2)
    rod7 = Rod(start_node=node8, end_node=node6)
    rod8 = Rod(start_node=node8, end_node=node9)
    rod9 = Rod(start_node=node10, end_node=node8)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node10, number_of_reactions=2, rotation=90)

    if load_index == 1:
        rod2 = Rod(start_node=node2, end_node=node4, stiffness=i3)
        load_P = Force(name='P', node=node5, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod8, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod9, value=q, rotation=180)
        loads = [load_P, load_q1, load_q2]
        nodes = [node1, node2, node4, node5, node6, node7, node8, node9, node10]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9]
    else:
        rod2_1 = Rod(start_node=node2, end_node=node3, stiffness=i3)
        rod2_2 = Rod(start_node=node3, end_node=node4, stiffness=i3)
        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_P2 = Force(name='P', node=node9, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4, rod5, rod6, rod7, rod8, rod9]

    supports = [support1, support2]

    return nodes, rods, supports, loads


def create_primary_system_22(params: dict):
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
    node2 = Node(name='2', x=0, y=h1)
    node3 = Node(name='3', x=l1 * 0.5, y=h1 + h2 * 0.75)
    node4 = Node(name='4', x=l1, y=h1 + h2 * 1.5)
    node5 = Node(name='K', x=l1 + l2 * 0.5, y=h1 + h2 * 1.5)
    node6 = Node(name='C', x=l1 + l2, y=h1 + h2 * 1.5, is_hinge=True)
    node7_1 = Node(name='D_1', x=l1 - 0.001, y=h1)
    node7_2 = Node(name='D_2', x=l1 + 0.001, y=h1)
    node8 = Node(name='8', x=l1 + l2, y=h1)
    node9 = Node(name='9', x=l1 * 1.3 + l2, y=h1)
    node10 = Node(name='B', x=l1 + l2, y=0)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod3 = Rod(start_node=node4, end_node=node5, stiffness=i3)
    rod4 = Rod(start_node=node5, end_node=node6, stiffness=i3)
    rod5 = Rod(start_node=node2, end_node=node7_1, stiffness=i2)
    rod6 = Rod(start_node=node7_2, end_node=node8, stiffness=i2)
    rod7 = Rod(start_node=node8, end_node=node6)
    rod8 = Rod(start_node=node8, end_node=node9)
    rod9 = Rod(start_node=node10, end_node=node8)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node10, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1_1 = Force(name='x1', node=node7_1, value=1, rotation=180)
    load_x1_2 = Force(name='x1', node=node7_2, value=1, rotation=0)
    load_x2_1 = Force(name='x2', node=node7_1, value=1, rotation=270)
    load_x2_2 = Force(name='x2', node=node7_2, value=1, rotation=90)
    load_x3 = Momentum(name='x3', node=node1, value=1, rotation=False)
    load_k = Force(name='x', node=node5, value=1, rotation=270)


    if load_index == 1:
        rod2 = Rod(start_node=node2, end_node=node4, stiffness=i3)
        load_P = Force(name='P', node=node5, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod8, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod9, value=q, rotation=180)
        loads_p = [load_P, load_q1, load_q2]
        nodes = [node1, node2, node4, node5, node6, node7_1, node7_2, node8, node9, node10]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9]
    else:
        rod2_1 = Rod(start_node=node2, end_node=node3, stiffness=i3)
        rod2_2 = Rod(start_node=node3, end_node=node4, stiffness=i3)
        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_P2 = Force(name='P', node=node9, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        loads_p = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7_1, node7_2, node8, node9, node10]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4, rod5, rod6, rod7, rod8, rod9]

    loads['1'] = [load_x1_1, load_x1_2]
    loads['2'] = [load_x2_1, load_x2_2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2]

    return nodes, rods, supports, loads


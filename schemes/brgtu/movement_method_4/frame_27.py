from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support


def create_frame_27(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    m = params["m"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='2', x=l1, y=0)
    node3 = Node(name='3', x=l1, y=h1 * 0.5 + h2 * 0.5)
    node4 = Node(name='B', x=0, y=h1 * 0.5 + h2 * 0.5)
    node5 = Node(name='5', x=l1 / 3, y=h1 * 0.5 + h2 * 0.5)
    node6 = Node(name='6', x=l1 * 2 / 3, y=h1 * 0.5 + h2 * 0.5)
    node7 = Node(name='7', x=l1, y=h1 * 0.5 + h2 * 0.8)
    node8 = Node(name='8', x=l1 + l2 * 0.3, y=h1 * 0.5 + h2 * 0.8)
    node9 = Node(name='C', x=l1 + l2, y=h1 * 0.5 + h2 * 0.5)
    node10 = Node(name='10', x=l1 + l2 * 0.5, y=0)
    node11 = Node(name='D', x=l1 + l2, y=0)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod3 = Rod(start_node=node2, end_node=node3)
    rod5 = Rod(start_node=node3, end_node=node7)
    rod6 = Rod(start_node=node7, end_node=node8)
    rod7 = Rod(start_node=node3, end_node=node9, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node4, number_of_reactions=1, rotation=90)
    support3 = Support(node=node9, number_of_reactions=3, rotation=180)
    support4 = Support(node=node11, number_of_reactions=1, rotation=90)

    if load_index == 1:
        rod2 = Rod(start_node=node2, end_node=node11, stiffness=i2)
        rod4_1 = Rod(start_node=node4, end_node=node5, stiffness=i3)
        rod4_2 = Rod(start_node=node5, end_node=node6, stiffness=i3)
        rod4_3 = Rod(start_node=node6, end_node=node3, stiffness=i3)

        load_P1 = Force(name='P', node=node5, value=P, rotation=270)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=180)
        load_q2 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node11, value=m, rotation=True)
        loads = [load_P1, load_P2, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node11]
        rods = [rod1, rod2, rod3, rod4_1, rod4_2, rod4_3, rod5, rod6, rod7]

    else:
        rod2_1 = Rod(start_node=node2, end_node=node10, stiffness=i2)
        rod2_2 = Rod(start_node=node10, end_node=node11, stiffness=i2)
        rod4 = Rod(start_node=node4, end_node=node3, stiffness=i3)

        load_P1 = Force(name='P', node=node8, value=P, rotation=90)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node10, value=m, rotation=False)
        loads = [load_P1, load_q1, load_m1]
        nodes = [node1, node2, node3, node7, node8, node9, node10, node11]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4, rod5, rod6, rod7]

    supports = [support1, support2, support3, support4]

    return nodes, rods, supports, loads


def create_fm_primary_system_27(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    m = params["m"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='2', x=l1, y=0)
    node3 = Node(name='3', x=l1, y=h1 * 0.5 + h2 * 0.5)
    node4 = Node(name='B', x=0, y=h1 * 0.5 + h2 * 0.5)
    node5 = Node(name='5', x=l1 / 3, y=h1 * 0.5 + h2 * 0.5)
    node6 = Node(name='6', x=l1 * 2 / 3, y=h1 * 0.5 + h2 * 0.5)
    node7 = Node(name='7', x=l1, y=h1 * 0.5 + h2 * 0.8)
    node8 = Node(name='8', x=l1 + l2 * 0.3, y=h1 * 0.5 + h2 * 0.8)
    node9 = Node(name='C', x=l1 + l2, y=h1 * 0.5 + h2 * 0.5)
    node10 = Node(name='10', x=l1 + l2 * 0.5, y=0)
    node11 = Node(name='D', x=l1 + l2, y=0)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
    rod3 = Rod(start_node=node2, end_node=node3)
    rod5 = Rod(start_node=node3, end_node=node7)
    rod6 = Rod(start_node=node7, end_node=node8)
    rod7 = Rod(start_node=node3, end_node=node9, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)

    loads = dict()
    load_x1 = Momentum(name='x1', node=node9, value=1, rotation=False)
    load_x2 = Force(name='x2', node=node9, value=1, rotation=0)
    load_x3 = Force(name='x3', node=node9, value=1, rotation=90)
    load_x4 = Force(name='x4', node=node4, value=1, rotation=90)
    load_x5 = Force(name='x5', node=node11, value=1, rotation=90)
    loads_s = [load_x1, load_x2, load_x3, load_x4, load_x5]

    if load_index == 1:
        rod2 = Rod(start_node=node2, end_node=node11, stiffness=i2)
        rod4_1 = Rod(start_node=node4, end_node=node5, stiffness=i3)
        rod4_2 = Rod(start_node=node5, end_node=node6, stiffness=i3)
        rod4_3 = Rod(start_node=node6, end_node=node3, stiffness=i3)

        load_P1 = Force(name='P', node=node5, value=P, rotation=270)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=180)
        load_q2 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node11, value=m, rotation=True)
        loads_p = [load_P1, load_P2, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node11]
        rods = [rod1, rod2, rod3, rod4_1, rod4_2, rod4_3, rod5, rod6, rod7]

    else:
        rod2_1 = Rod(start_node=node2, end_node=node10, stiffness=i2)
        rod2_2 = Rod(start_node=node10, end_node=node11, stiffness=i2)
        rod4 = Rod(start_node=node4, end_node=node3, stiffness=i3)

        load_P1 = Force(name='P', node=node8, value=P, rotation=90)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node10, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]
        nodes = [node1, node2, node3, node7, node8, node9, node10, node11]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4, rod5, rod6, rod7]

    loads['s'] = loads_s
    loads['p'] = loads_p

    supports = [support1]

    return nodes, rods, supports, loads


def create_mm_primary_system_27(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    m = params["m"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='1', x=0, y=0)
    node2 = Node(name='2', x=l1, y=0)
    node3 = Node(name='3', x=l1, y=h1 * 0.5 + h2 * 0.5)
    node4 = Node(name='4', x=0, y=h1 * 0.5 + h2 * 0.5)
    node5 = Node(name='0', x=l1 / 3, y=h1 * 0.5 + h2 * 0.5)
    node6 = Node(name='0', x=l1 * 2 / 3, y=h1 * 0.5 + h2 * 0.5)
    node7 = Node(name='5', x=l1, y=h1 * 0.5 + h2 * 0.8)
    node8 = Node(name='6', x=l1 + l2 * 0.3, y=h1 * 0.5 + h2 * 0.8)
    node9 = Node(name='7', x=l1 + l2, y=h1 * 0.5 + h2 * 0.5)
    node10 = Node(name='0', x=l1 + l2 * 0.5, y=0)
    node11 = Node(name='8', x=l1 + l2, y=0)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node2, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=i2)
    rod2 = RodForMovementMethod(start_node=node2, end_node=node11, start_support_type='Жесткий', end_support_type='Шарнирный', stiffness=i2)
    rod3 = RodForMovementMethod(start_node=node2, end_node=node3, start_support_type='Жесткий', end_support_type='Жесткий')
    rod4 = RodForMovementMethod(start_node=node4, end_node=node3, start_support_type='Шарнирный', end_support_type='Жесткий', stiffness=i3)
    rod5 = RodForMovementMethod(start_node=node3, end_node=node7, start_support_type='Жесткий', end_support_type='Нет')
    rod6 = RodForMovementMethod(start_node=node7, end_node=node8, start_support_type='Жесткий', end_support_type='Нет')
    rod7 = RodForMovementMethod(start_node=node3, end_node=node9, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node4, number_of_reactions=1, rotation=90)
    support3 = Support(node=node9, number_of_reactions=3, rotation=180)
    support4 = Support(node=node11, number_of_reactions=1, rotation=90)

    if load_index == 1:
        load_P1 = Force(name='P', node=node5, value=P, rotation=270)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', start_coordinates=(node7.x, node7.y), end_coordinates=(node8.x, node8.y), value=q, rotation=270)
        load_q2 = DistributedForce(name='q', start_coordinates=(node2.x, node2.y), end_coordinates=(node3.x, node3.y), value=q, rotation=180)
        load_m1 = Momentum(name='m', node=node11, value=m, rotation=True)
        loads_p = [load_P1, load_P2, load_q1, load_q2, load_m1]

    else:
        load_P1 = Force(name='P', node=node8, value=P, rotation=90)
        load_q1 = DistributedForce(name='q', start_coordinates=(node1.x, node1.y), end_coordinates=(node2.x, node2.y), value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node10, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]

    nodes = [node1, node2, node3, node4, node7, node8, node9, node11]
    rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]

    loads = {}
    load_z1 = Twist(name='z1', node=node2)
    load_z2 = Twist(name='z2', node=node3)
    load_z3 = Displacement(name='z3', node=node2, value=1, rotation=90)

    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['3'] = [load_z3]
    loads['p'] = loads_p

    supports = [support1, support2, support3, support4]

    return nodes, rods, supports, loads

from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support


def create_frame_17(params: dict):
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

    node1 = Node(name='A', x=l1 / 3, y=0)
    node2 = Node(name='2', x=l1 / 3, y=h1 * 0.5)
    node3 = Node(name='3', x=l1 / 3, y=h1)
    node4 = Node(name='4', x=l1 / 3, y=h1 + h2 * 0.5)
    node6 = Node(name='5', x=l1 / 3, y=h1 + h2)
    node5 = Node(name='6', x=0, y=h1 + h2)
    node7 = Node(name='7', x=l1 / 3 + l1 * 0.5, y=h1 + h2)
    node8 = Node(name='8', x=l1 / 3 + l1 * 0.5 + l2 * 0.5, y=h1 + h2)
    node9 = Node(name='C', x=l1 / 3 + l1 * 0.5 + l2 * 0.5, y=h1, is_hinge=True)
    node10 = Node(name='10', x=l1 / 3 + l1 * 0.5 + l2, y=h1 + h2)
    node11 = Node(name='11', x=l1 / 3 + l1 + l2, y=h1 + h2)
    node12 = Node(name='12', x=l1 * 2 / 3 + l1 + l2, y=h1 + h2)
    node13 = Node(name='13', x=l1 / 3 + l1 + l2, y=h1 + h2 * 0.5)
    node14 = Node(name='E', x=l1 / 3 + l1 + l2, y=h1)
    node15 = Node(name='15', x=l1 / 3 + l1 + l2, y=h1 * 0.5)
    node16 = Node(name='T', x=l1 / 3 + l1 + l2, y=0)

    rod3 = Rod(start_node=node6, end_node=node5, stiffness=i3)
    rod5 = Rod(start_node=node9, end_node=node8)
    rod6 = Rod(start_node=node3, end_node=node9, stiffness=i2)
    rod7 = Rod(start_node=node9, end_node=node14, stiffness=i2)
    rod9 = Rod(start_node=node11, end_node=node12, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node16, number_of_reactions=3, rotation=90)

    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)
        rod2 = Rod(start_node=node3, end_node=node5)
        rod4 = Rod(start_node=node5, end_node=node8, stiffness=i3)
        rod8 = Rod(start_node=node8, end_node=node11, stiffness=i3)
        rod10 = Rod(start_node=node14, end_node=node11)
        rod11_1 = Rod(start_node=node15, end_node=node14)
        rod11_2 = Rod(start_node=node16, end_node=node15)

        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_P2 = Force(name='P', node=node15, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_q3 = DistributedForce(name='q', rod=rod8, value=q, rotation=270)
        load_q4 = DistributedForce(name='q', rod=rod9, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node9, value=m, rotation=True)
        load_m2 = Momentum(name='m', node=node9, value=m, rotation=False)
        loads = [load_P1, load_P2, load_q1, load_q2, load_q3, load_q4, load_m1, load_m2]
        nodes = [node1, node2, node3, node5, node6, node8, node9, node11, node12, node14, node15, node16]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11_1, rod11_2]

    else:
        rod1 = Rod(start_node=node1, end_node=node3)
        rod2_1 = Rod(start_node=node3, end_node=node4)
        rod2_2 = Rod(start_node=node4, end_node=node5)
        rod4_1 = Rod(start_node=node5, end_node=node7, stiffness=i3)
        rod4_2 = Rod(start_node=node7, end_node=node8, stiffness=i3)
        rod8_1 = Rod(start_node=node8, end_node=node10, stiffness=i3)
        rod8_2 = Rod(start_node=node10, end_node=node11, stiffness=i3)
        rod10_1 = Rod(start_node=node13, end_node=node11)
        rod10_2 = Rod(start_node=node14, end_node=node13)
        rod11 = Rod(start_node=node16, end_node=node14)

        load_P1 = Force(name='P', node=node4, value=P, rotation=0)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_P3 = Force(name='P', node=node12, value=P, rotation=270)
        load_P4 = Force(name='P', node=node13, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod5, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod7, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node7, value=m, rotation=False)
        load_m2 = Momentum(name='m', node=node10, value=m, rotation=True)
        loads = [load_P1, load_P2, load_P3, load_P4, load_q1, load_q2, load_m1, load_m2]
        nodes = [node1, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node16]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4_1, rod4_2, rod5, rod6, rod7, rod8_1, rod8_2, rod9, rod10_1, rod10_2, rod11]

    supports = [support1, support2]

    return nodes, rods, supports, loads


def create_fm_primary_system_17(params: dict):
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


    node1 = Node(name='A', x=l1 / 3, y=0)
    node2 = Node(name='2', x=l1 / 3, y=h1 * 0.5)
    node3 = Node(name='3', x=l1 / 3, y=h1)
    node4 = Node(name='4', x=l1 / 3, y=h1 + h2 * 0.5)
    node5 = Node(name='5', x=l1 / 3, y=h1 + h2)
    node6 = Node(name='6', x=0, y=h1 + h2)
    node7 = Node(name='7', x=l1 / 3 + l1 * 0.5, y=h1 + h2)
    node8 = Node(name='8', x=l1 / 3 + l1 * 0.5 + l2 * 0.5, y=h1 + h2)
    node9 = Node(name='C', x=l1 / 3 + l1 * 0.5 + l2 * 0.5, y=h1)

    rod3 = Rod(start_node=node6, end_node=node5, stiffness=i3)
    rod5 = Rod(start_node=node3, end_node=node9, stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node8, value=1, rotation=90)
    load_x2 = Force(name='x2', node=node8, value=1, rotation=180)
    load_x3 = Momentum(name='x3', node=node8, value=1, rotation=False)
    load_x4 = Force(name='x4', node=node9, value=1, rotation=90)
    load_x5 = Force(name='x5', node=node9, value=1, rotation=180)
    loads_s = [load_x1, load_x2, load_x3, load_x4, load_x5]

    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)
        rod2 = Rod(start_node=node3, end_node=node5)
        rod4 = Rod(start_node=node5, end_node=node8, stiffness=i3)

        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node9, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node5, node6, node8, node9]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5]

    else:
        rod1 = Rod(start_node=node1, end_node=node3)
        rod2_1 = Rod(start_node=node3, end_node=node4)
        rod2_2 = Rod(start_node=node4, end_node=node5)
        rod4_1 = Rod(start_node=node5, end_node=node7, stiffness=i3)
        rod4_2 = Rod(start_node=node7, end_node=node8, stiffness=i3)

        load_P1 = Force(name='P', node=node4, value=P, rotation=0)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod5, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node7, value=m, rotation=False)
        loads_p = [load_P1, load_P2, load_q1, load_m1]
        nodes = [node1, node3, node4, node5, node6, node7, node8, node9]
        rods = [rod1, rod2_1, rod2_2, rod3, rod4_1, rod4_2, rod5]

    loads['s'] = loads_s
    loads['p'] = loads_p
    supports = [support1]

    return nodes, rods, supports, loads


def create_mm_primary_system_17(params: dict):
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

    node1 = Node(name='1', x=l1 / 3, y=0)
    node2 = Node(name='0', x=l1 / 3, y=h1 * 0.5)
    node3 = Node(name='2', x=l1 / 3, y=h1)
    node4 = Node(name='0', x=l1 / 3, y=h1 + h2 * 0.5)
    node5 = Node(name='3', x=l1 / 3, y=h1 + h2)
    node6 = Node(name='4', x=0, y=h1 + h2)
    node7 = Node(name='0', x=l1 / 3 + l1 * 0.5, y=h1 + h2)
    node8 = Node(name='5', x=l1 / 3 + l1 * 0.5 + l2 * 0.5, y=h1 + h2)
    node9 = Node(name='6', x=l1 / 3 + l1 * 0.5 + l2 * 0.5, y=h1)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node3, start_support_type='Жесткий', end_support_type='Жесткий')
    rod2 = RodForMovementMethod(start_node=node3, end_node=node5, start_support_type='Жесткий', end_support_type='Жесткий')
    rod3 = RodForMovementMethod(start_node=node6, end_node=node5, start_support_type='Нет', end_support_type='Жесткий', stiffness=i3)
    rod4 = RodForMovementMethod(start_node=node5, end_node=node8, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=i3)
    rod5 = RodForMovementMethod(start_node=node3, end_node=node9, start_support_type='Жесткий', end_support_type='Шарнирный', stiffness=i2)
    rod6 = RodForMovementMethod(start_node=node9, end_node=node8, start_support_type='Шарнирный', end_support_type='Жесткий', stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node8, number_of_reactions=3, rotation=180)
    support3 = Support(node=node9, number_of_reactions=2, rotation=90)

    if load_index == 1:
        load_P1 = Force(name='P', node=node2, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', start_coordinates=(node6.x, node6.y), end_coordinates=(node8.x, node8.y), value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node9, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]
    else:
        load_P1 = Force(name='P', node=node4, value=P, rotation=0)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', start_coordinates=(node3.x, node3.y), end_coordinates=(node9.x, node9.y), value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node7, value=m, rotation=False)
        loads_p = [load_P1, load_P2, load_q1, load_m1]

    nodes = [node1, node2, node3, node5, node7, node8, node9]
    rods = [rod1, rod2, rod3, rod4, rod5, rod6]

    loads = {}
    load_z1 = Twist(name='z1', node=node3)
    load_z2 = Twist(name='z2', node=node5)
    load_z3 = Displacement(name='z3', node=node9, value=1, rotation=90)

    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['3'] = [load_z3]
    loads['p'] = loads_p

    supports = [support1, support2, support3]

    return nodes, rods, supports, loads


from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support


def create_frame_14(params: dict):
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
    node2 = Node(name='2', x=0, y=h1)
    node3 = Node(name='B', x=l1, y=h1)
    node4 = Node(name='4', x=0, y=h1 + h2 / 3)
    node5 = Node(name='5', x=0, y=h1 + h2 * 2 / 3)
    node6 = Node(name='D', x=0, y=h1 + h2, is_hinge=True)
    node7 = Node(name='7', x=l1, y=h1 + h2)
    node8 = Node(name='8', x=l1, y=h1 + h2 * 0.5)
    node9 = Node(name='E', x=l1 + l2, y=h1 + h2, is_hinge=True)
    node10 = Node(name='C', x=l1 + l2, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=i2)
    rod4 = Rod(start_node=node6, end_node=node7, stiffness=i3)
    rod5_1 = Rod(start_node=node3, end_node=node8)
    rod5_2 = Rod(start_node=node8, end_node=node7)
    rod6 = Rod(start_node=node7, end_node=node9, stiffness=i3)
    rod7 = Rod(start_node=node10, end_node=node9)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node3, number_of_reactions=3, rotation=90)
    support3 = Support(node=node10, number_of_reactions=3, rotation=90)

    if load_index == 1:
        rod3 = Rod(start_node=node2, end_node=node6)

        load_P1 = Force(name='P', node=node8, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node6, value=m, rotation=False, rod=rod3)
        loads = [load_P1, load_q1, load_m1]
        nodes = [node1, node2, node3, node6, node7, node8, node9, node10]
        rods = [rod1, rod2, rod3, rod4, rod5_1, rod5_2, rod6, rod7]

    else:
        rod3_1 = Rod(start_node=node2, end_node=node4)
        rod3_2 = Rod(start_node=node4, end_node=node5)
        rod3_3 = Rod(start_node=node5, end_node=node6)

        load_P1 = Force(name='P', node=node4, value=P, rotation=0)
        load_P2 = Force(name='P', node=node5, value=P, rotation=0)
        load_P3 = Force(name='P', node=node9, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod7, value=q, rotation=180)
        load_m1 = Momentum(name='m', node=node8, value=m, rotation=False)
        loads = [load_P1, load_P2, load_P3, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10]
        rods = [rod1, rod2, rod3_1, rod3_2, rod3_3, rod4, rod5_1, rod5_2, rod6, rod7]

    supports = [support1, support2, support3]

    symmetry = None
    details = dict()
    details['node_name_for_static_check'] = 'D'

    return nodes, rods, supports, loads, symmetry, details


def create_fm_primary_system_14(params: dict):
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
    node2 = Node(name='2', x=0, y=h1)
    node3 = Node(name='B', x=l1, y=h1)
    node4 = Node(name='4', x=0, y=h1 + h2 / 3)
    node5 = Node(name='5', x=0, y=h1 + h2 * 2 / 3)
    node6_1 = Node(name='D1', x=0, y=h1 + h2)
    node6_2 = Node(name='D2', x=0, y=h1 + h2)
    node7 = Node(name='7', x=l1, y=h1 + h2)
    node8 = Node(name='8', x=l1, y=h1 + h2 * 0.5)
    node9 = Node(name='E', x=l1 + l2, y=h1 + h2, is_hinge=True)
    node10 = Node(name='C', x=l1 + l2, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=i2)
    rod4 = Rod(start_node=node6_2, end_node=node7, stiffness=i3)
    rod5_1 = Rod(start_node=node3, end_node=node8)
    rod5_2 = Rod(start_node=node8, end_node=node7)
    rod6 = Rod(start_node=node7, end_node=node9, stiffness=i3)
    rod7 = Rod(start_node=node10, end_node=node9)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node10, number_of_reactions=2, rotation=90)

    loads = dict()
    load_x1 = Momentum(name='x1', node=node10, value=1, rotation=False)
    load_x2 = Force(name='x2', node=node6_1, value=1, rotation=0)
    load_x3 = Force(name='x2', node=node6_2, value=1, rotation=180)
    load_x4 = Force(name='x3', node=node6_1, value=1, rotation=90)
    load_x5 = Force(name='x3', node=node6_2, value=1, rotation=270)
    load_x6 = Momentum(name='x4', node=node3, value=1, rotation=False)
    load_x7 = Force(name='x5', node=node3, value=1, rotation=0)
    load_x8 = Force(name='x6', node=node3, value=1, rotation=90)

    loads_s = [load_x1, load_x2, load_x3, load_x4, load_x5, load_x6, load_x7, load_x8]

    if load_index == 1:
        rod3 = Rod(start_node=node2, end_node=node6_1)

        load_P1 = Force(name='P', node=node8, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node6_1, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]
        nodes = [node1, node2, node3, node6_1, node6_2, node7, node8, node9, node10]
        rods = [rod1, rod2, rod3, rod4, rod5_1, rod5_2, rod6, rod7]

    else:
        rod3_1 = Rod(start_node=node2, end_node=node4)
        rod3_2 = Rod(start_node=node4, end_node=node5)
        rod3_3 = Rod(start_node=node5, end_node=node6_1)

        load_P1 = Force(name='P', node=node4, value=P, rotation=0)
        load_P2 = Force(name='P', node=node5, value=P, rotation=0)
        load_P3 = Force(name='P', node=node9, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod7, value=q, rotation=180)
        load_m1 = Momentum(name='m', node=node8, value=m, rotation=False)
        loads_p = [load_P1, load_P2, load_P3, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6_1, node6_2, node7, node8, node9, node10]
        rods = [rod1, rod2, rod3_1, rod3_2, rod3_3, rod4, rod5_1, rod5_2, rod6, rod7]

    loads['s'] = loads_s
    loads['p'] = loads_p

    supports = [support1, support2]

    details = dict()
    details['equation_of_static_determinacy'] = ' 3 · 3 - 3 = 6'

    return nodes, rods, supports, loads, details


def create_mm_primary_system_14(params: dict):
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
    node2 = Node(name='2', x=0, y=h1)
    node3 = Node(name='3', x=l1, y=h1)
    node4 = Node(name='0', x=0, y=h1 + h2 / 3)
    node5 = Node(name='0', x=0, y=h1 + h2 * 2 / 3)
    node6 = Node(name='4', x=0, y=h1 + h2, is_hinge=True)
    node7 = Node(name='5', x=l1, y=h1 + h2)
    node8 = Node(name='0', x=l1, y=h1 + h2 * 0.5)
    node9 = Node(name='6', x=l1 + l2, y=h1 + h2, is_hinge=True)
    node10 = Node(name='7', x=l1 + l2, y=h1)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node2, start_support_type='Шарнирный', end_support_type='Жесткий')
    rod2 = RodForMovementMethod(start_node=node2, end_node=node3, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=i2)
    rod3 = RodForMovementMethod(start_node=node2, end_node=node6, start_support_type='Жесткий', end_support_type='Шарнирный')
    rod4 = RodForMovementMethod(start_node=node6, end_node=node7, start_support_type='Шарнирный', end_support_type='Жесткий', stiffness=i3)
    rod5 = RodForMovementMethod(start_node=node3, end_node=node7, start_support_type='Жесткий', end_support_type='Жесткий')
    rod6 = RodForMovementMethod(start_node=node7, end_node=node9, start_support_type='Жесткий', end_support_type='Шарнирный', stiffness=i3)
    rod7 = RodForMovementMethod(start_node=node10, end_node=node9, start_support_type='Жесткий', end_support_type='Шарнирный')

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node3, number_of_reactions=3, rotation=90)
    support3 = Support(node=node10, number_of_reactions=3, rotation=90)

    if load_index == 1:
        load_P1 = Force(name='P', node=node8, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', start_coordinates=(node1.x, node1.y), end_coordinates=(node2.x, node2.y), value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node6, value=m, rotation=False, rod=rod3)
        loads_p = [load_P1, load_q1, load_m1]
    else:
        load_P1 = Force(name='P', node=node4, value=P, rotation=0)
        load_P2 = Force(name='P', node=node5, value=P, rotation=0)
        load_P3 = Force(name='P', node=node9, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', start_coordinates=(node6.x, node6.y), end_coordinates=(node7.x, node7.y), value=q, rotation=270)
        load_q2 = DistributedForce(name='q', start_coordinates=(node10.x, node10.y), end_coordinates=(node9.x, node9.y), value=q, rotation=180)
        load_m1 = Momentum(name='m', node=node8, value=m, rotation=False)
        loads_p = [load_P1, load_P2, load_P3, load_q1, load_q2, load_m1]

    nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10]
    rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]

    loads = {}
    load_z1 = Twist(name='z1', node=node2)
    load_z2 = Twist(name='z2', node=node7)
    load_z3 = Displacement(name='z3', node=node6, value=1, rotation=0)
    # load_z4 = Twist(name='z4', node=node3)


    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['3'] = [load_z3]
    # loads['4'] = [load_z4]
    loads['p'] = loads_p

    supports = [support1, support2, support3]

    details = dict()
    details['equation_of_static_determinacy'] = ' 2 + 1 = 3'

    return nodes, rods, supports, loads, details

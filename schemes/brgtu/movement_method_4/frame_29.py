from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support


def create_frame_29(params: dict):
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

    node1 = Node(name='A', x=l1 * 0.3, y=0)
    node2 = Node(name='2', x=l1 * 0.3, y=h1 / 3)
    node3 = Node(name='3', x=l1 * 0.3, y=h1 * 2 / 3)
    node4 = Node(name='4', x=l1 * 0.3, y=h1)
    node5 = Node(name='5', x=0, y=h1)
    node6 = Node(name='6', x=0, y=h1 * 2 / 3)
    node7 = Node(name='B', x=l1 * 0.3 + l2, y=h1)
    node8 = Node(name='8', x=l1 * 0.3, y=h1 + h2 * 0.5)
    node9 = Node(name='9', x=l1 * 0.3, y=h1 + h2)
    node10 = Node(name='10', x=0, y=h1 + h2)
    node11 = Node(name='D', x=l1 * 0.5 + l2, y=h1 + h2)

    rod2 = Rod(start_node=node5, end_node=node4, stiffness=i2)
    rod3 = Rod(start_node=node6, end_node=node5)
    rod4 = Rod(start_node=node4, end_node=node7, stiffness=i2)
    rod6 = Rod(start_node=node10, end_node=node9)
    rod7 = Rod(start_node=node9, end_node=node11, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=1, rotation=90)
    support3 = Support(node=node11, number_of_reactions=3, rotation=180)

    symmetry = None

    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)
        rod1_3 = Rod(start_node=node3, end_node=node4)
        rod5_1 = Rod(start_node=node4, end_node=node8)
        rod5_2 = Rod(start_node=node8, end_node=node9)

        load_P1 = Force(name='P', node=node2, value=P, rotation=180)
        load_P2 = Force(name='P', node=node3, value=P, rotation=180)
        load_P3 = Force(name='P', node=node7, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod7, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node8, value=m, rotation=False)
        loads = [load_P1, load_P2, load_P3, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11]
        rods = [rod1_1, rod1_2, rod1_3, rod2, rod3, rod4, rod5_1, rod5_2, rod6, rod7]

    else:
        rod1 = Rod(start_node=node1, end_node=node4)
        rod5_1 = Rod(start_node=node4, end_node=node8)
        rod5_2 = Rod(start_node=node8, end_node=node9)

        load_P1 = Force(name='P', node=node8, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node1, value=m, rotation=True)
        loads = [load_P1, load_q1, load_q2, load_m1]
        nodes = [node1, node4, node5, node6, node7, node8, node9, node10, node11]
        rods = [rod1, rod2, rod3, rod4, rod5_1, rod5_2, rod6, rod7]

    supports = [support1, support2, support3]

    details = dict()
    details['node_name_for_static_check'] = 'B'

    return nodes, rods, supports, loads, symmetry, details


def create_fm_primary_system_29(params: dict):
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

    node1 = Node(name='A', x=l1 * 0.3, y=0)
    node2 = Node(name='2', x=l1 * 0.3, y=h1 / 3)
    node3 = Node(name='3', x=l1 * 0.3, y=h1 * 2 / 3)
    node4 = Node(name='4', x=l1 * 0.3, y=h1)
    node5 = Node(name='5', x=0, y=h1)
    node6 = Node(name='6', x=0, y=h1 * 2 / 3)
    node7 = Node(name='B', x=l1 * 0.3 + l2, y=h1)
    node8 = Node(name='8', x=l1 * 0.3, y=h1 + h2 * 0.5)
    node9 = Node(name='9', x=l1 * 0.3, y=h1 + h2)
    node10 = Node(name='10', x=0, y=h1 + h2)
    node11 = Node(name='D', x=l1 * 0.5 + l2, y=h1 + h2)

    rod2 = Rod(start_node=node5, end_node=node4, stiffness=i2)
    rod3 = Rod(start_node=node6, end_node=node5)
    rod4 = Rod(start_node=node4, end_node=node7, stiffness=i2)
    rod6 = Rod(start_node=node10, end_node=node9)
    rod7 = Rod(start_node=node9, end_node=node11, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=1, rotation=90)

    loads = dict()
    load_x1 = Momentum(name='x1', node=node11, value=1, rotation=False)
    load_x2 = Force(name='x2', node=node11, value=1, rotation=0)
    load_x3 = Force(name='x3', node=node11, value=1, rotation=90)
    loads_s = [load_x1, load_x2, load_x3]

    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2)
        rod1_2 = Rod(start_node=node2, end_node=node3)
        rod1_3 = Rod(start_node=node3, end_node=node4)
        rod5_1 = Rod(start_node=node4, end_node=node8)
        rod5_2 = Rod(start_node=node8, end_node=node9)

        load_P1 = Force(name='P', node=node2, value=P, rotation=180)
        load_P2 = Force(name='P', node=node3, value=P, rotation=180)
        load_P3 = Force(name='P', node=node7, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod6, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod7, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node8, value=m, rotation=False)
        loads_p = [load_P1, load_P2, load_P3, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11]
        rods = [rod1_1, rod1_2, rod1_3, rod2, rod3, rod4, rod5_1, rod5_2, rod6, rod7]

    else:
        rod1 = Rod(start_node=node1, end_node=node4)
        rod5_1 = Rod(start_node=node4, end_node=node8)
        rod5_2 = Rod(start_node=node8, end_node=node9)

        load_P1 = Force(name='P', node=node8, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node1, value=m, rotation=True)
        loads_p = [load_P1, load_q1, load_q2, load_m1]
        nodes = [node1, node4, node5, node6, node7, node8, node9, node10, node11]
        rods = [rod1, rod2, rod3, rod4, rod5_1, rod5_2, rod6, rod7]

    loads['s'] = loads_s
    loads['p'] = loads_p

    supports = [support1, support2]

    details = dict()
    details['equation_of_static_determinacy'] = ' 3 · 2 - 3 = 3'

    return nodes, rods, supports, loads, details


def create_mm_primary_system_29(params: dict):
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

    node1 = Node(name='1', x=l1 * 0.3, y=0)
    node2 = Node(name='0', x=l1 * 0.3, y=h1 / 3)
    node3 = Node(name='0', x=l1 * 0.3, y=h1 * 2 / 3)
    node4 = Node(name='2', x=l1 * 0.3, y=h1)
    node5 = Node(name='3', x=0, y=h1)
    node6 = Node(name='4', x=0, y=h1 * 2 / 3)
    node7 = Node(name='5', x=l1 * 0.3 + l2, y=h1)
    node8 = Node(name='0', x=l1 * 0.3, y=h1 + h2 * 0.5)
    node9 = Node(name='6', x=l1 * 0.3, y=h1 + h2)
    node10 = Node(name='7', x=0, y=h1 + h2)
    node11 = Node(name='8', x=l1 * 0.5 + l2, y=h1 + h2)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node4, start_support_type='Шарнирный', end_support_type='Жесткий')
    rod2 = RodForMovementMethod(start_node=node5, end_node=node4, start_support_type='Нет', end_support_type='Жесткий', stiffness=i2)
    rod3 = RodForMovementMethod(start_node=node6, end_node=node5, start_support_type='Нет', end_support_type='Жесткий')
    rod4 = RodForMovementMethod(start_node=node4, end_node=node7, start_support_type='Жесткий', end_support_type='Шарнирный', stiffness=i2)
    rod5 = RodForMovementMethod(start_node=node4, end_node=node9, start_support_type='Жесткий', end_support_type='Жесткий')
    rod6 = RodForMovementMethod(start_node=node10, end_node=node9, start_support_type='Нет', end_support_type='Жесткий')
    rod7 = RodForMovementMethod(start_node=node9, end_node=node11, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node7, number_of_reactions=1, rotation=90)
    support3 = Support(node=node11, number_of_reactions=3, rotation=180)

    if load_index == 1:
        load_P1 = Force(name='P', node=node2, value=P, rotation=180)
        load_P2 = Force(name='P', node=node3, value=P, rotation=180)
        load_P3 = Force(name='P', node=node7, value=P, rotation=0)
        load_m1 = Momentum(name='m', node=node8, value=m, rotation=False)
        load_q1 = DistributedForce(name='q', start_coordinates=(node10.x, node10.y), end_coordinates=(node11.x, node11.y), value=q, rotation=270)
        loads_p = [load_P1, load_P2, load_P3, load_q1, load_m1]

    else:
        load_P1 = Force(name='P', node=node8, value=P, rotation=180)
        load_m1 = Momentum(name='m', node=node1, value=m, rotation=True)
        load_q1 = DistributedForce(name='q', start_coordinates=(node6.x, node6.y), end_coordinates=(node5.x, node5.y), value=q, rotation=0)
        load_q2 = DistributedForce(name='q', start_coordinates=(node4.x, node4.y), end_coordinates=(node7.x, node7.y), value=q, rotation=270)
        loads_p = [load_P1, load_q1, load_q2, load_m1]

    nodes = [node1, node4, node5, node6, node7, node9, node10, node11]
    rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]

    loads = {}
    load_z1 = Twist(name='z1', node=node4)
    load_z2 = Twist(name='z2', node=node9)
    load_z3 = Displacement(name='z3', node=node5, value=1, rotation=0)

    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['3'] = [load_z3]
    loads['p'] = loads_p

    supports = [support1, support2, support3]

    details = dict()
    details['equation_of_static_determinacy'] = ' 2 + 1 = 3'

    return nodes, rods, supports, loads, details

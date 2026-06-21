from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support


def create_frame_21(params: dict):
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
    node2 = Node(name='2', x=l1 * 0.5, y=0)
    node3 = Node(name='3', x=l1, y=0)
    node4 = Node(name='4', x=l1, y=h1)
    node5 = Node(name='B', x=0, y=h1)
    node6 = Node(name='6', x=l1, y=h1 + h2 * 0.5)
    node7 = Node(name='C', x=l1, y=h1 + h2)
    node8 = Node(name='8', x=l1 + l2 / 3, y=h1)
    node9 = Node(name='9', x=l1 + l2 * 0.5, y=h1)
    node10 = Node(name='10', x=l1 + l2 * 2 / 3, y=h1)
    node11 = Node(name='11', x=l1 + l2, y=h1)
    node12 = Node(name='T', x=l1 + l2, y=h1 + h2 * 0.5)
    node13 = Node(name='D', x=l1 + l2, y=h1 + h2)
    node14 = Node(name='E', x=l1 * 2 + l2, y=h1)
    node15 = Node(name='15', x=l1 + l2, y=0)
    node16 = Node(name='16', x=l1 * 1.5 + l2, y=0)
    node17 = Node(name='T', x=l1 * 2 + l2, y=0)

    symmetry = ('x', node9)

    rod2 = Rod(start_node=node3, end_node=node4)
    rod3 = Rod(start_node=node5, end_node=node4, stiffness=i3)
    rod8 = Rod(start_node=node11, end_node=node14, stiffness=i3)
    rod9 = Rod(start_node=node15, end_node=node11)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node5, number_of_reactions=1, rotation=90)
    support3 = Support(node=node7, number_of_reactions=1, rotation=0)
    support4 = Support(node=node13, number_of_reactions=1, rotation=180)
    support5 = Support(node=node14, number_of_reactions=1, rotation=90)
    support6 = Support(node=node17, number_of_reactions=3, rotation=180)


    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
        rod1_2 = Rod(start_node=node2, end_node=node3, stiffness=i2)
        rod4_1 = Rod(start_node=node4, end_node=node6)
        rod4_2 = Rod(start_node=node6, end_node=node7)
        rod5 = Rod(start_node=node4, end_node=node9, stiffness=i3)
        rod6 = Rod(start_node=node9, end_node=node11, stiffness=i3)
        rod7_1 = Rod(start_node=node11, end_node=node12)
        rod7_2 = Rod(start_node=node12, end_node=node13)
        rod10_1 = Rod(start_node=node15, end_node=node16, stiffness=i2)
        rod10_2 = Rod(start_node=node16, end_node=node17, stiffness=i2)

        load_P1 = Force(name='P', node=node6, value=P, rotation=0)
        load_P2 = Force(name='P', node=node12, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod8, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node2, value=m, rotation=False)
        load_m2 = Momentum(name='m', node=node16, value=m, rotation=True)
        loads = [load_P1, load_P2, load_q1, load_q2, load_m1, load_m2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node9, node11, node12, node13, node14, node15, node16, node17]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4_1, rod4_2, rod5, rod6, rod7_1, rod7_2, rod8, rod9, rod10_1, rod10_2]

    else:
        rod1 = Rod(start_node=node1, end_node=node3, stiffness=i2)
        rod4 = Rod(start_node=node4, end_node=node7)
        rod5_1 = Rod(start_node=node4, end_node=node8, stiffness=i3)
        rod5_2 = Rod(start_node=node8, end_node=node9, stiffness=i3)
        rod6_1 = Rod(start_node=node9, end_node=node10, stiffness=i3)
        rod6_2 = Rod(start_node=node10, end_node=node11, stiffness=i3)
        rod7 = Rod(start_node=node11, end_node=node13)
        rod10 = Rod(start_node=node15, end_node=node17, stiffness=i2)


        load_P1 = Force(name='P', node=node8, value=P, rotation=270)
        load_P2 = Force(name='P', node=node10, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod10, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node5, value=m, rotation=False)
        load_m2 = Momentum(name='m', node=node14, value=m, rotation=True)
        loads = [load_P1, load_P2, load_q1, load_q2, load_m1, load_m2]
        nodes = [node1, node3, node4, node5, node7, node8, node9, node10, node11, node13, node14, node15, node17]
        rods = [rod1, rod2, rod3, rod4, rod5_1, rod5_2, rod6_1, rod6_2, rod7, rod8, rod9, rod10]

    supports = [support1, support2, support3, support4, support5, support6]

    details = dict()
    details['node_name_for_static_check'] = 'B'

    return nodes, rods, supports, loads, symmetry, details


def create_fm_primary_system_21(params: dict):
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
    node2 = Node(name='2', x=l1 * 0.5, y=0)
    node3 = Node(name='3', x=l1, y=0)
    node4 = Node(name='4', x=l1, y=h1)
    node5 = Node(name='B', x=0, y=h1)
    node6 = Node(name='6', x=l1, y=h1 + h2 * 0.5)
    node7 = Node(name='C', x=l1, y=h1 + h2)
    node8 = Node(name='8', x=l1 + l2 / 3, y=h1)
    node9 = Node(name='9', x=l1 + l2 * 0.5, y=h1)

    rod2 = Rod(start_node=node3, end_node=node4)
    rod3 = Rod(start_node=node5, end_node=node4, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)

    loads = {}
    load_x1 = Momentum(name='x1', node=node9, value=1, rotation=False)
    load_x2 = Force(name='x2', node=node9, value=1, rotation=0)
    load_x3 = Force(name='x3', node=node5, value=1, rotation=90)
    load_x4 = Force(name='x4', node=node7, value=1, rotation=0)
    loads_s = [load_x1, load_x2, load_x3, load_x4]

    if load_index == 1:
        rod1_1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
        rod1_2 = Rod(start_node=node2, end_node=node3, stiffness=i2)
        rod4_1 = Rod(start_node=node4, end_node=node6)
        rod4_2 = Rod(start_node=node6, end_node=node7)
        rod5 = Rod(start_node=node4, end_node=node9, stiffness=i3)

        load_P1 = Force(name='P', node=node6, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod3, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node2, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node9]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4_1, rod4_2, rod5]

    else:
        rod1 = Rod(start_node=node1, end_node=node3, stiffness=i2)
        rod4 = Rod(start_node=node4, end_node=node7)
        rod5_1 = Rod(start_node=node4, end_node=node8, stiffness=i3)
        rod5_2 = Rod(start_node=node8, end_node=node9, stiffness=i3)

        load_P1 = Force(name='P', node=node8, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node5, value=m, rotation=False)
        loads = [load_P1, load_q1, load_m1]
        nodes = [node1, node3, node4, node5, node7, node8, node9]
        rods = [rod1, rod2, rod3, rod4, rod5_1, rod5_2]

    loads['s'] = loads_s
    loads['p'] = loads_p
    supports = [support1]

    details = dict()
    details['equation_of_static_determinacy'] = ' 3 · 5 - 8 = 7'

    return nodes, rods, supports, loads, details


def create_mm_primary_system_21(params: dict):
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
    node2 = Node(name='0', x=l1 * 0.5, y=0)
    node3 = Node(name='2', x=l1, y=0)
    node4 = Node(name='3', x=l1, y=h1)
    node5 = Node(name='4', x=0, y=h1)
    node6 = Node(name='0', x=l1, y=h1 + h2 * 0.5)
    node7 = Node(name='5', x=l1, y=h1 + h2)
    node8 = Node(name='0', x=l1 + l2 / 3, y=h1)
    node9 = Node(name='6', x=l1 + l2 * 0.5, y=h1)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node3, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=i2)
    rod2 = RodForMovementMethod(start_node=node3, end_node=node4, start_support_type='Жесткий', end_support_type='Жесткий')
    rod3 = RodForMovementMethod(start_node=node5, end_node=node4, start_support_type='Шарнирный', end_support_type='Жесткий', stiffness=i3)
    rod4 = RodForMovementMethod(start_node=node4, end_node=node7, start_support_type='Жесткий', end_support_type='Шарнирный')
    rod5 = RodForMovementMethod(start_node=node4, end_node=node9, start_support_type='Жесткий', end_support_type='Скользящий', stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node5, number_of_reactions=1, rotation=90)
    support3 = Support(node=node7, number_of_reactions=1, rotation=0)
    support4 = Support(node=node9, number_of_reactions=4, rotation=180)

    if load_index == 1:
        load_P1 = Force(name='P', node=node6, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', start_coordinates=(node5.x, node5.y), end_coordinates=(node4.x, node4.y), value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node2, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]
    else:
        load_P1 = Force(name='P', node=node8, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', start_coordinates=(node1.x, node1.y), end_coordinates=(node3.x, node3.y), value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node5, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]

    nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
    rods = [rod1, rod2, rod3, rod4, rod5]

    loads = {}
    load_z1 = Twist(name='z1', node=node3)
    load_z2 = Twist(name='z2', node=node4)
    load_z3 = Displacement(name='z3', node=node3, value=1, rotation=90)

    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['3'] = [load_z3]
    loads['p'] = loads_p

    supports = [support1, support2, support3, support4]

    details = dict()
    details['equation_of_static_determinacy'] = ' 4 + 3 = 7'

    return nodes, rods, supports, loads, details


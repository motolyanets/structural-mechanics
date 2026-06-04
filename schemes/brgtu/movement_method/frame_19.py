from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support


def create_frame_19(params: dict):
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

    node1 = Node(name='A', x=0, y=h1)
    node2 = Node(name='E', x=0, y=h1 + h2, is_hinge=True)
    node3 = Node(name='3', x=l1, y=h1 + h2)
    node4 = Node(name='4', x=l1, y=h1 + h2 * 0.5)
    node5 = Node(name='5', x=l1, y=h1)
    node6 = Node(name='B', x=l1, y=0)
    node7 = Node(name='7', x=l1 + l2 * 0.5, y=h1)
    node8 = Node(name='8', x=l1 + l2, y=h1)
    node9 = Node(name='C', x=l1 + l2, y=0)
    node10 = Node(name='10', x=l1 + l2, y=h1 + h2 * 0.5)
    node11 = Node(name='11', x=l1 + l2, y=h1 + h2)
    node12 = Node(name='T', x=l1 * 2 + l2, y=h1 + h2, is_hinge=True)
    node13 = Node(name='D', x=l1 * 2 + l2, y=h1)

    symmetry = ('x', node7)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=i3)
    rod3_1 = Rod(start_node=node4, end_node=node3)
    rod3_2 = Rod(start_node=node5, end_node=node4)
    rod4 = Rod(start_node=node6, end_node=node5)
    rod5 = Rod(start_node=node5, end_node=node7, stiffness=i2)
    rod6 = Rod(start_node=node7, end_node=node8, stiffness=i2)
    rod7 = Rod(start_node=node9, end_node=node8)
    rod8_1 = Rod(start_node=node8, end_node=node10)
    rod8_2 = Rod(start_node=node10, end_node=node11)
    rod9 = Rod(start_node=node11, end_node=node12, stiffness=i3)
    rod10 = Rod(start_node=node13, end_node=node12)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node6, number_of_reactions=2, rotation=90)
    support3 = Support(node=node9, number_of_reactions=2, rotation=90)
    support4 = Support(node=node13, number_of_reactions=3, rotation=90)


    if load_index == 1:
        load_P1 = Force(name='P', node=node7, value=P, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod10, value=q, rotation=180)
        load_m1 = Momentum(name='m', node=node4, value=m, rotation=False)
        load_m2 = Momentum(name='m', node=node10, value=m, rotation=True)
        loads = [load_P1, load_q1, load_q2, load_m1, load_m2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
        rods = [rod1, rod2, rod3_1, rod3_2, rod4, rod5, rod6, rod7, rod8_1, rod8_2, rod9, rod10]

    else:
        load_P1 = Force(name='P', node=node4, value=P, rotation=180)
        load_P2 = Force(name='P', node=node10, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod4, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod7, value=q, rotation=180)
        load_m1 = Momentum(name='m', node=node2, value=m, rotation=True, rod=rod1)
        load_m2 = Momentum(name='m', node=node12, value=m, rotation=False, rod=rod10)
        loads = [load_P1, load_P2, load_q1, load_q2, load_m1, load_m2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
        rods = [rod1, rod2, rod3_1, rod3_2, rod4, rod5, rod6, rod7, rod8_1, rod8_2, rod9, rod10]

    supports = [support1, support2, support3, support4]

    return nodes, rods, supports, loads, symmetry


def create_fm_primary_system_19(params: dict):
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


    node1 = Node(name='A', x=0, y=h1)
    node2 = Node(name='E', x=0, y=h1 + h2, is_hinge=True)
    node3 = Node(name='3', x=l1, y=h1 + h2)
    node4 = Node(name='4', x=l1, y=h1 + h2 * 0.5)
    node5 = Node(name='5', x=l1, y=h1)
    node6 = Node(name='B', x=l1, y=0)
    node7 = Node(name='7', x=l1 + l2 * 0.5, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=i3)
    rod3_1 = Rod(start_node=node5, end_node=node4)
    rod3_2 = Rod(start_node=node4, end_node=node3)
    rod4 = Rod(start_node=node6, end_node=node5)
    rod5 = Rod(start_node=node5, end_node=node7, stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=2, rotation=90)
    support2 = Support(node=node6, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1 = Momentum(name='x1', node=node1, value=1, rotation=False)
    load_x2 = Force(name='x2', node=node7, value=1, rotation=0)
    load_x3 = Momentum(name='x3', node=node7, value=1, rotation=False)
    loads_s = [load_x1, load_x2, load_x3]

    if load_index == 1:
        load_P1 = Force(name='P', node=node7, value=P / 2, rotation=270)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node4, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7]
        rods = [rod1, rod2, rod3_1, rod3_2, rod4, rod5]

    else:
        load_P1 = Force(name='P', node=node4, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod4, value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node2, value=m, rotation=True, rod=rod1)
        loads_p = [load_P1, load_q1, load_m1]
        nodes = [node1, node2, node3, node4, node5, node6, node7]
        rods = [rod1, rod2, rod3_1, rod3_2, rod4, rod5]

    loads['s'] = loads_s
    loads['p'] = loads_p
    supports = [support1, support2]

    return nodes, rods, supports, loads


def create_mm_primary_system_19(params: dict):
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

    node1 = Node(name='1', x=0, y=h1)
    node2 = Node(name='2', x=0, y=h1 + h2, is_hinge=True)
    node3 = Node(name='3', x=l1, y=h1 + h2)
    node4 = Node(name='0', x=l1, y=h1 + h2 * 0.5)
    node5 = Node(name='4', x=l1, y=h1)
    node6 = Node(name='5', x=l1, y=0)
    node7 = Node(name='6', x=l1 + l2 * 0.5, y=h1)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node2, start_support_type='Жесткий', end_support_type='Шарнирный')
    rod2 = RodForMovementMethod(start_node=node2, end_node=node3, start_support_type='Шарнирный', end_support_type='Жесткий', stiffness=i3)
    rod3 = RodForMovementMethod(start_node=node5, end_node=node3, start_support_type='Жесткий', end_support_type='Жесткий')
    rod4 = RodForMovementMethod(start_node=node6, end_node=node5, start_support_type='Шарнирный', end_support_type='Жесткий')
    rod5 = RodForMovementMethod(start_node=node5, end_node=node7, start_support_type='Жесткий', end_support_type='Скользящий', stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node6, number_of_reactions=2, rotation=90)
    support3 = Support(node=node7, number_of_reactions=4, rotation=180)

    if load_index == 1:
        load_P1 = Force(name='P', node=node7, value=P / 2, rotation=270)
        load_q1 = DistributedForce(name='q', start_coordinates=(node1.x, node1.y), end_coordinates=(node2.x, node2.y), value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node4, value=m, rotation=False)
        loads_p = [load_P1, load_q1, load_m1]
    else:
        load_P1 = Force(name='P', node=node4, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', start_coordinates=(node6.x, node6.y), end_coordinates=(node5.x, node5.y), value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node2, value=m, rotation=True, rod=rod1)
        loads_p = [load_P1, load_q1, load_m1]

    nodes = [node1, node2, node3, node4, node5, node6, node7]
    rods = [rod1, rod2, rod3, rod4, rod5]

    loads = {}
    load_z1 = Twist(name='z1', node=node3)
    load_z2 = Twist(name='z2', node=node5)
    load_z3 = Displacement(name='z3', node=node2, value=1, rotation=0)

    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['3'] = [load_z3]
    loads['p'] = loads_p

    supports = [support1, support2, support3]

    return nodes, rods, supports, loads


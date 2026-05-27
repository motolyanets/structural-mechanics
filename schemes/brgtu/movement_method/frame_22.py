from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support
from services.services import is_point_on_rod, is_distr_force_on_rod


def create_frame_22(params: dict):
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
    node3 = Node(name='3', x=0, y=h1 + h2 * 0.3)
    node4 = Node(name='4', x=l1 / 3, y=h1)
    node5 = Node(name='5', x=l1 / 2, y=h1)
    node6 = Node(name='6', x=l1 * 2 / 3, y=h1)
    node7 = Node(name='7', x=l1, y=h1)
    node8 = Node(name='B', x=l1, y=h1 + h2)
    node9 = Node(name='C', x=l1 + l2, y=h1)
    node10 = Node(name='E', x=l1, y=0, is_hinge=True)
    node11 = Node(name='11', x=l1 + l2 * 0.5, y=0)
    node12 = Node(name='D', x=l1 + l2, y=0)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3)
    rod4 = Rod(start_node=node7, end_node=node8)
    rod5 = Rod(start_node=node7, end_node=node9, stiffness=i3)
    rod6 = Rod(start_node=node10, end_node=node7)
    rod7 = Rod(start_node=node10, end_node=node11, stiffness=i2)
    rod8 = Rod(start_node=node11, end_node=node12, stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node8, number_of_reactions=1, rotation=180)
    support3 = Support(node=node9, number_of_reactions=2, rotation=180)
    support4 = Support(node=node12, number_of_reactions=3, rotation=180)

    if load_index == 1:
        rod3_1 = Rod(start_node=node2, end_node=node4, stiffness=i3)
        rod3_2 = Rod(start_node=node4, end_node=node6, stiffness=i3)
        rod3_3 = Rod(start_node=node6, end_node=node7, stiffness=i3)

        load_P1 = Force(name='P', node=node4, value=P, rotation=270)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_P3 = Force(name='P', node=node10, value=P, rotation=90)
        load_q1 = DistributedForce(name='q', rod=rod1, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod2, value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node11, value=m, rotation=True)
        loads = [load_P1, load_P2, load_P3, load_q1, load_q2, load_m1]
        nodes = [node1, node2, node3, node4, node6, node7, node8, node9, node10, node11, node12]
        rods = [rod1, rod2, rod3_1, rod3_2, rod3_3, rod4, rod5, rod6, rod7, rod8]

    else:
        rod3_1 = Rod(start_node=node2, end_node=node5, stiffness=i3)
        rod3_2 = Rod(start_node=node5, end_node=node7, stiffness=i3)

        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_P2 = Force(name='P', node=node11, value=P, rotation=90)
        load_q1 = DistributedForce(name='q', rod=rod5, value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node5, value=m, rotation=False)
        loads = [load_P1, load_P2, load_q1, load_m1]
        nodes = [node1, node2, node3, node5, node7, node8, node9, node10, node11, node12]
        rods = [rod1, rod2, rod3_1, rod3_2, rod4, rod5, rod6, rod7, rod8]

    supports = [support1, support2, support3, support4]

    return nodes, rods, supports, loads


def create_mm_primary_system_22(params: dict):
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
    node3 = Node(name='3', x=0, y=h1 + h2 * 0.3)
    node4 = Node(name='0', x=l1 / 3, y=h1)
    node5 = Node(name='0', x=l1 / 2, y=h1)
    node6 = Node(name='0', x=l1 * 2 / 3, y=h1)
    node7 = Node(name='4', x=l1, y=h1)
    node8 = Node(name='5', x=l1, y=h1 + h2)
    node9 = Node(name='6', x=l1 + l2, y=h1)
    node10 = Node(name='7', x=l1, y=0, is_hinge=True)
    node11 = Node(name='0', x=l1 + l2 * 0.5, y=0)
    node12 = Node(name='8', x=l1 + l2, y=0)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node2, start_support_type='Жесткий', end_support_type='Жесткий')
    rod2 = RodForMovementMethod(start_node=node2, end_node=node3, start_support_type='Жесткий', end_support_type='Нет')
    rod3 = RodForMovementMethod(start_node=node2, end_node=node7, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=i3)
    rod4 = RodForMovementMethod(start_node=node7, end_node=node8, start_support_type='Жесткий', end_support_type='Шарнирный')
    rod5 = RodForMovementMethod(start_node=node7, end_node=node9, start_support_type='Жесткий', end_support_type='Шарнирный', stiffness=i3)
    rod6 = RodForMovementMethod(start_node=node10, end_node=node7, start_support_type='Шарнирный', end_support_type='Жесткий')
    rod7 = RodForMovementMethod(start_node=node10, end_node=node12, start_support_type='Шарнирный', end_support_type='Жесткий', stiffness=i2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=90)
    support2 = Support(node=node8, number_of_reactions=1, rotation=180)
    support3 = Support(node=node9, number_of_reactions=2, rotation=180)
    support4 = Support(node=node12, number_of_reactions=3, rotation=180)

    if load_index == 1:
        load_P1 = Force(name='P', node=node4, value=P, rotation=270)
        load_P2 = Force(name='P', node=node6, value=P, rotation=270)
        load_P3 = Force(name='P', node=node10, value=P, rotation=90)
        load_q1 = DistributedForce(name='q', start_coordinates=(node1.x, node1.y), end_coordinates=(node3.x, node3.y), value=q, rotation=0)
        load_m1 = Momentum(name='m', node=node11, value=m, rotation=True)
        loads_p = [load_P1, load_P2, load_P3, load_q1, load_m1]

    else:
        load_P1 = Force(name='P', node=node3, value=P, rotation=0)
        load_P2 = Force(name='P', node=node11, value=P, rotation=90)
        load_q1 = DistributedForce(name='q', start_coordinates=(node7.x, node7.y), end_coordinates=(node9.x, node9.y), value=q, rotation=270)
        load_m1 = Momentum(name='m', node=node5, value=m, rotation=False)
        loads_p = [load_P1, load_P2, load_q1, load_m1]

    nodes = [node1, node2, node3, node5, node7, node8, node9, node10, node11, node12]
    rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7]

    loads = {}
    load_z1 = Twist(name='z1', node=node2)
    load_z2 = Twist(name='z2', node=node7)
    load_z3 = Displacement(name='z3', node=node10, value=1, rotation=90)

    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['3'] = [load_z3]
    loads['p'] = loads_p

    supports = [support1, support2, support3, support4]

    return nodes, rods, supports, loads


def create_fm_primary_system_22(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='2', x=0, y=h1)
    node3 = Node(name='3', x=0, y=h1 + h2 * 0.3)
    node4 = Node(name='4', x=l1 / 3, y=h1)
    node5 = Node(name='5', x=l1 / 2, y=h1)
    node6 = Node(name='6', x=l1 * 2 / 3, y=h1)
    node7 = Node(name='7', x=l1, y=h1)
    node8 = Node(name='B', x=l1, y=h1 + h2)
    node9 = Node(name='C', x=l1 + l2, y=h1)
    node10 = Node(name='E', x=l1, y=0, is_hinge=True)
    node11 = Node(name='11', x=l1 + l2 * 0.5, y=0)
    node12 = Node(name='D', x=l1 + l2, y=0)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3)
    rod4 = Rod(start_node=node7, end_node=node8)
    rod5 = Rod(start_node=node7, end_node=node9, stiffness=i3)
    rod6 = Rod(start_node=node10, end_node=node7)
    rod7 = Rod(start_node=node10, end_node=node11, stiffness=i2)
    rod8 = Rod(start_node=node11, end_node=node12, stiffness=i2)

    support1 = Support(node=node8, number_of_reactions=1, rotation=180)
    support2 = Support(node=node12, number_of_reactions=3, rotation=180)

    load_x1 = Momentum(name='x1', node=node1, value=1, rotation=False)
    load_x2 = Force(name='x2', node=node1, value=1, rotation=0)
    load_x3 = Force(name='x3', node=node1, value=1, rotation=90)
    load_x4 = Force(name='x4', node=node9, value=1, rotation=90)
    load_x5 = Force(name='x5', node=node9, value=1, rotation=180)
    loads = [load_x1, load_x2, load_x3, load_x4, load_x5]

    if load_index == 1:
        rod3_1 = Rod(start_node=node2, end_node=node4, stiffness=i3)
        rod3_2 = Rod(start_node=node4, end_node=node6, stiffness=i3)
        rod3_3 = Rod(start_node=node6, end_node=node7, stiffness=i3)

        nodes = [node1, node2, node3, node4, node6, node7, node8, node9, node10, node11, node12]
        rods = [rod1, rod2, rod3_1, rod3_2, rod3_3, rod4, rod5, rod6, rod7, rod8]

    else:
        rod3_1 = Rod(start_node=node2, end_node=node5, stiffness=i3)
        rod3_2 = Rod(start_node=node5, end_node=node7, stiffness=i3)

        nodes = [node1, node2, node3, node5, node7, node8, node9, node10, node11, node12]
        rods = [rod1, rod2, rod3_1, rod3_2, rod4, rod5, rod6, rod7, rod8]

    supports = [support1, support2]

    return nodes, rods, supports, loads

from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support


def create_frame_25(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    P = params["P"]
    q = params["q"]

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='E', x=l1, y=0, is_hinge=True)
    node3 = Node(name='B', x=l1 + l2, y=0)
    node4 = Node(name='C', x=0, y=h1)
    node5 = Node(name='5', x=l1 / 2, y=h1)
    node6 = Node(name='6', x=l1, y=h1)
    node7 = Node(name='7', x=l1 + l2 * 0.5, y=h1)
    node8 = Node(name='D', x=l1 + l2, y=h1)

    symmetry = None

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=3)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=3)
    rod3 = Rod(start_node=node2, end_node=node6)
    rod4_1 = Rod(start_node=node4, end_node=node5, stiffness=2)
    rod4_2 = Rod(start_node=node5, end_node=node6, stiffness=2)
    rod5_1 = Rod(start_node=node6, end_node=node7, stiffness=2)
    rod5_2 = Rod(start_node=node7, end_node=node8, stiffness=2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node3, number_of_reactions=1, rotation=90)
    support3 = Support(node=node4, number_of_reactions=3, rotation=0)
    support4 = Support(node=node8, number_of_reactions=1, rotation=90)

    load_P1 = Force(name='P', node=node5, value=P, rotation=270)
    load_P2 = Force(name='P', node=node7, value=P, rotation=270)
    load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
    loads = [load_P1, load_P2, load_q1]
    nodes = [node1, node2, node3, node4, node5, node6, node7, node8]
    rods = [rod1, rod2, rod3, rod4_1, rod4_2, rod5_1, rod5_2]

    supports = [support1, support2, support3, support4]

    details = dict()
    details['node_name_for_static_check'] = 'E'

    return nodes, rods, supports, loads, symmetry, details


def create_fm_primary_system_25(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    P = params["P"]
    q = params["q"]

    node1 = Node(name='A', x=0, y=0)
    node2 = Node(name='E', x=l1, y=0, is_hinge=True)
    node3 = Node(name='B', x=l1 + l2, y=0)
    node4 = Node(name='C', x=0, y=h1)
    node5 = Node(name='5', x=l1 / 2, y=h1)
    node6 = Node(name='6', x=l1, y=h1)
    node7 = Node(name='7', x=l1 + l2 * 0.5, y=h1)
    node8 = Node(name='D', x=l1 + l2, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2, stiffness=3)
    rod2 = Rod(start_node=node2, end_node=node3, stiffness=3)
    rod3 = Rod(start_node=node2, end_node=node6)
    rod4_1 = Rod(start_node=node4, end_node=node5, stiffness=2)
    rod4_2 = Rod(start_node=node5, end_node=node6, stiffness=2)
    rod5_1 = Rod(start_node=node6, end_node=node7, stiffness=2)
    rod5_2 = Rod(start_node=node7, end_node=node8, stiffness=2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node3, number_of_reactions=1, rotation=90)
    support3 = Support(node=node8, number_of_reactions=1, rotation=90)

    supports = [support1, support2, support3]

    loads = {}
    load_x1 = Momentum(name='x1', node=node4, value=1, rotation=False)
    load_x2 = Force(name='x2', node=node4, value=1, rotation=0)
    load_x3 = Force(name='x2', node=node4, value=1, rotation=90)
    loads_s = [load_x1, load_x2, load_x3]

    load_P1 = Force(name='P', node=node5, value=P, rotation=270)
    load_P2 = Force(name='P', node=node7, value=P, rotation=270)
    load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=270)
    loads_p = [load_P1, load_P2, load_q1]
    nodes = [node1, node2, node3, node4, node5, node6, node7, node8]
    rods = [rod1, rod2, rod3, rod4_1, rod4_2, rod5_1, rod5_2]

    loads['s'] = loads_s
    loads['p'] = loads_p

    details = dict()
    details['equation_of_static_determinacy'] = ' 3 · 3 - 6 = 3'
    details['splitted_frames_order'] = (
        ['C', '5', '6', '7', 'D', 'E1'],
        ['E2', 'B'],
        ['A', 'E']
    )

    return nodes, rods, supports, loads, details


def create_mm_primary_system_25(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    P = params["P"]
    q = params["q"]

    node1 = Node(name='1', x=0, y=0)
    node2 = Node(name='2', x=l1, y=0, is_hinge=True)
    node3 = Node(name='3', x=l1 + l2, y=0)
    node4 = Node(name='4', x=0, y=h1)
    node5 = Node(name='0', x=l1 / 2, y=h1)
    node6 = Node(name='5', x=l1, y=h1)
    node7 = Node(name='0', x=l1 + l2 * 0.5, y=h1)
    node8 = Node(name='6', x=l1 + l2, y=h1)

    rod1 = RodForMovementMethod(start_node=node1, end_node=node2, start_support_type='Жесткий', end_support_type='Шарнирный', stiffness=3)
    rod2 = RodForMovementMethod(start_node=node2, end_node=node3, start_support_type='Шарнирный', end_support_type='Шарнирный', stiffness=3)
    rod3 = RodForMovementMethod(start_node=node2, end_node=node6, start_support_type='Шарнирный', end_support_type='Жесткий')
    rod4 = RodForMovementMethod(start_node=node4, end_node=node6, start_support_type='Жесткий', end_support_type='Жесткий', stiffness=2)
    rod5 = RodForMovementMethod(start_node=node6, end_node=node8, start_support_type='Жесткий', end_support_type='Шарнирный', stiffness=2)

    support1 = Support(node=node1, number_of_reactions=3, rotation=0)
    support2 = Support(node=node3, number_of_reactions=1, rotation=90)
    support3 = Support(node=node4, number_of_reactions=3, rotation=0)
    support4 = Support(node=node8, number_of_reactions=1, rotation=90)


    load_P1 = Force(name='P', node=node5, value=P, rotation=270)
    load_P2 = Force(name='P', node=node7, value=P, rotation=270)
    load_q1 = DistributedForce(name='q', start_coordinates=(node2.x, node2.y), end_coordinates=(node3.x, node3.y), value=q, rotation=270)
    loads_p = [load_P1, load_P2, load_q1]

    nodes = [node1, node2, node3, node4, node5, node6, node7]
    rods = [rod1, rod2, rod3, rod4, rod5]

    loads = {}
    load_z1 = Twist(name='z1', node=node6)
    load_z2 = Displacement(name='z2', node=node2, value=1, rotation=90)

    loads['1'] = [load_z1]
    loads['2'] = [load_z2]
    loads['p'] = loads_p

    supports = [support1, support2, support3, support4]

    details = dict()
    details['equation_of_static_determinacy'] = ' 1 + 1 = 2'

    return nodes, rods, supports, loads, details


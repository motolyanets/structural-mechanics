from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.solver import SolvableFrame
from core.mechanics.support import Support


def create_frame_10(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=h1)
    node2 = Node(name='2', x=l1 * 0.25, y=h1)
    node3 = Node(name='3', x=l1 * 0.5, y=h1)
    node4 = Node(name='K', x=l1 * 0.5, y=h1 * 0.5)
    node5 = Node(name='B', x=l1 * 0.5, y=0)
    node6 = Node(name='6', x=l1 * 0.5 + l2, y=h1 + h2 * 0.5)
    node7 = Node(name='L', x=l1 * 0.5 + l2, y=h1 * 0.8, is_hinge=True)
    node8 = Node(name='C', x=l1 * 0.5 + l2, y=0)
    node9 = Node(name='D', x=l1 * 1.5 + l2, y=0)
    node10 = Node(name='S', x=l1 * 1.5 + l2, y=h1 * 0.8, is_hinge=True)
    node11 = Node(name='11', x=l1 * 1.5 + l2, y=h1 + h2 * 0.5)
    node12 = Node(name='12', x=l1 * 1.5 + l2 * 2, y=h1)
    node13 = Node(name='13', x=l1 * 1.5 + l2 * 2, y=h1 * 0.5)
    node14 = Node(name='E', x=l1 * 1.5 + l2 * 2, y=0)
    node15 = Node(name='15', x=l1 * 1.75 + l2 * 2, y=h1)
    node16 = Node(name='T', x=l1 * 2 + l2 * 2, y=h1)

    rod2 = Rod(start_node=node4, end_node=node3)
    rod3 = Rod(start_node=node5, end_node=node4)
    rod4 = Rod(start_node=node3, end_node=node6, stiffness=i3)
    rod5 = Rod(start_node=node7, end_node=node6)
    rod6 = Rod(start_node=node8, end_node=node7)
    rod7 = Rod(start_node=node7, end_node=node10, is_start_hinge=True, is_end_hinge=True)
    rod8 = Rod(start_node=node9, end_node=node10)
    rod9 = Rod(start_node=node10, end_node=node11)
    rod10 = Rod(start_node=node11, end_node=node12, stiffness=i3)

    support1 = Support(node=node1, number_of_reactions=1, rotation=90)
    support2 = Support(node=node5, number_of_reactions=2, rotation=90)
    support3 = Support(node=node8, number_of_reactions=3, rotation=90)
    support4 = Support(node=node9, number_of_reactions=3, rotation=90)
    support5 = Support(node=node14, number_of_reactions=2, rotation=90)
    support6 = Support(node=node16, number_of_reactions=1, rotation=90)

    if load_index == 1:
        rod1 = Rod(start_node=node1, end_node=node3, stiffness=i2)
        rod11_1 = Rod(start_node=node13, end_node=node12)
        rod11_2 = Rod(start_node=node14, end_node=node13)
        rod12 = Rod(start_node=node12, end_node=node16, stiffness=i2)

        load_P1 = Force(name='P', node=node4, value=P, rotation=0)
        load_P2 = Force(name='P', node=node13, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        load_q2 = DistributedForce(name='q', rod=rod10, value=q, rotation=270)
        loads = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node3, node4, node5, node6, node7, node8, node9, node11, node12, node13, node14, node16]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11_1, rod11_2, rod12]

    else:
        rod1_1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
        rod1_2 = Rod(start_node=node2, end_node=node3, stiffness=i2)
        rod11 = Rod(start_node=node14, end_node=node12)
        rod12_1 = Rod(start_node=node12, end_node=node15, stiffness=i2)
        rod12_2 = Rod(start_node=node15, end_node=node16, stiffness=i2)

        load_P1 = Force(name='P', node=node2, value=P, rotation=270)
        load_P2 = Force(name='P', node=node15, value=P, rotation=270)
        load_P3 = Force(name='P', node=node6, value=P, rotation=180)
        load_P4 = Force(name='P', node=node11, value=P, rotation=0)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod3, value=q, rotation=0)
        load_q3 = DistributedForce(name='q', rod=rod11, value=q, rotation=180)
        loads = [load_P1, load_P2, load_P3, load_P4, load_q1, load_q2, load_q3]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node14, node15, node16]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12_1, rod12_2]

    supports = [support1, support2, support3, support4, support5, support6]

    # return nodes, rods, supports, loads, calkulate_diagram_rods_order
    return nodes, rods, supports, loads


def create_primary_system_10(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    P = params["P"]
    q = params["q"]
    i2 = params["i2"]
    i3 = params["i3"]

    node1 = Node(name='A', x=0, y=h1)
    node2 = Node(name='2', x=l1 * 0.25, y=h1)
    node3 = Node(name='3', x=l1 * 0.5, y=h1)
    node4 = Node(name='K', x=l1 * 0.5, y=h1 * 0.5)
    node5 = Node(name='B', x=l1 * 0.5, y=0)
    node6 = Node(name='6', x=l1 * 0.5 + l2, y=h1 + h2 * 0.5)
    node7 = Node(name='L', x=l1 * 0.5 + l2, y=h1 * 0.8, is_hinge=True)
    node8 = Node(name='C', x=l1 * 0.5 + l2, y=0)

    rod2 = Rod(start_node=node4, end_node=node3)
    rod3 = Rod(start_node=node5, end_node=node4)
    rod4 = Rod(start_node=node3, end_node=node6, stiffness=i3)
    rod5 = Rod(start_node=node7, end_node=node6)
    rod6 = Rod(start_node=node8, end_node=node7)

    support1 = Support(node=node5, number_of_reactions=2, rotation=90)
    support2 = Support(node=node8, number_of_reactions=2, rotation=90)

    loads = {}
    load_x1 = Force(name='x1', node=node1, value=1, rotation=90)
    load_x2 = Force(name='x2', node=node7, value=1, rotation=180)
    load_x3 = Momentum(name='x3', node=node8, value=1, rotation=False)
    load_k = Force(name='x', node=node4, value=1, rotation=180)

    if load_index == 1:
        rod1 = Rod(start_node=node1, end_node=node3, stiffness=i2)

        load_P = Force(name='P', node=node4, value=P, rotation=0)
        load_q = DistributedForce(name='q', rod=rod4, value=q, rotation=270)
        loads_p = [load_P, load_q]
        nodes = [node1, node3, node4, node5, node6, node7, node8]
        rods = [rod1, rod2, rod3, rod4, rod5, rod6]

        # splitted_frames_for_diagram_order = (
        #     ['A', '2', '3'],
        #     ['B', 'K', '3'],
        #     ['A', '2', '3', 'B', 'K', '3', '6', 'L'],
        #     ['C', 'L'],
        # )

    else:
        rod1_1 = Rod(start_node=node1, end_node=node2, stiffness=i2)
        rod1_2 = Rod(start_node=node2, end_node=node3, stiffness=i2)

        load_P1 = Force(name='P', node=node2, value=P, rotation=270)
        load_P2 = Force(name='P', node=node6, value=P, rotation=180)
        load_q1 = DistributedForce(name='q', rod=rod2, value=q, rotation=0)
        load_q2 = DistributedForce(name='q', rod=rod3, value=q, rotation=0)
        loads_p = [load_P1, load_P2, load_q1, load_q2]
        nodes = [node1, node2, node3, node4, node5, node6, node7, node8]
        rods = [rod1_1, rod1_2, rod2, rod3, rod4, rod5, rod6]

        # splitted_frames_for_diagram_order = (
        #     [rod1_1, rod1_2],
        #     [rod2, rod3],
        #     [rod1_1, rod1_2, rod2, rod3, rod4, rod5.],
        #     [rod6],
        # )

    loads['1'] = [load_x1]
    loads['2'] = [load_x2]
    loads['3'] = [load_x3]
    loads['p'] = loads_p
    loads['k'] = [load_k]
    supports = [support1, support2]

    return nodes, rods, supports, loads
    # return nodes, rods, supports, loads, splitted_frames_for_diagram_order


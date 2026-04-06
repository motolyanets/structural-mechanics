from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.support import Support


def create_frame_29(params: dict):
    l1 = params["l1"]
    l2 = params["l2"]
    h1 = params["h1"]
    h2 = params["h2"]
    load_index = params["load_index"]
    F = params["F"]
    P = params["P"]
    q = params["q"]
    m = params["m"]

    node1 = Node(name="A", x=0, y=h1)
    node2 = Node(name="2", x=l1 / 2, y=h1)
    node3 = Node(name="3", x=l1 / 2, y=0)
    node4 = Node(name="4", x=l1 / 2, y=(h1 + h2) * 2)
    node5 = Node(name="D", x=l1 * 1.5, y=(h1 + h2) * 2)
    node6 = Node(name="6", x=l1 * 1.5, y=h1 * 2)
    node7 = Node(name="L", x=l1 * 1.5, y=h1)
    node8 = Node(name="B", x=l1 * 1.5, y=0)
    node9 = Node(name="E", x=l1 * 2.5, y=(h1 + h2) * 2, is_hinge=True)
    node10 = Node(name="10", x=l1 * 2.5 + l2, y=h1 * 2)
    node11 = Node(name="C", x=l1 * 2.5 + l2 * 1.5, y=h1 * 2)
    node12 = Node(name="T", x=l1 * 2.5 + l2, y=h1)
    node13 = Node(name="13", x=l1 * 2 + l2 * 0.5, y=h1)

    rod1 = Rod(start_node=node1, end_node=node2)
    rod2 = Rod(start_node=node2, end_node=node3)
    rod3 = Rod(start_node=node2, end_node=node4)
    rod4 = Rod(start_node=node4, end_node=node5, is_end_hinge=True)
    rod5 = Rod(start_node=node5, end_node=node6)
    rod6 = Rod(start_node=node6, end_node=node7)
    rod7 = Rod(start_node=node7, end_node=node8)
    rod8 = Rod(start_node=node5, end_node=node9)
    rod9 = Rod(start_node=node9, end_node=node10)
    rod10 = Rod(start_node=node10, end_node=node11)
    rod11 = Rod(start_node=node10, end_node=node12)
    rod12 = Rod(start_node=node12, end_node=node13, is_start_hinge=True)
    rod13 = Rod(start_node=node7, end_node=node13, is_start_hinge=True)

    support1 = Support(node=node1, number_of_reactions=1, rotation=90)
    support2 = Support(node=node8, number_of_reactions=2, rotation=90)
    support3 = Support(node=node11, number_of_reactions=1, rotation=90)

    if load_index == 1:
        load_P = Force(name='P', node=node3, value=P, rotation=180)
        load_F = Force(name='F', node=node13, value=F, rotation=270)
        load_m = Momentum(name='m', node=node6, value=m, rotation=True)
        load_q1 = DistributedForce(name='q1', rod=rod8, value=q, rotation=270)
        load_q2 = DistributedForce(name='q1', rod=rod9, value=q, rotation=270)
        loads = [load_P, load_F, load_m, load_q1, load_q2]
    else:
        load_P = Force(name='P', node=node6, value=P, rotation=0)
        load_F = Force(name='F', node=node12, value=F, rotation=270)
        load_m = Momentum(name='m', node=node9, value=m, rotation=True)
        load_q1 = DistributedForce(name='q1', rod=rod2, value=q, rotation=0)
        load_q2 = DistributedForce(name='q1', rod=rod3, value=q, rotation=0)
        loads = [load_P, load_F, load_m, load_q1, load_q2]

    nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13]
    rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8, rod9, rod10, rod11, rod12, rod13]
    supports = [support1, support2, support3]

    splitted_frames_order = (
        ['A', '2', '3', '4', 'D'],
        ['L', '13', 'T'],
        ['D', '6', 'L', 'B', 'E', '10', 'C', 'T']
    )

    return nodes, rods, supports, loads, splitted_frames_order
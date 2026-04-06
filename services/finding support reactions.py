from typing import List

from data_base.frames import Node, Rod, Force, Momentum, Support
from main_composite_frame import frame

nodes_old = frame.nodes
rods_old = frame.rods
supports_old = frame.supports
loads_old = frame.loads

nodes = nodes_old[:5]
rods = rods_old[:4]
supports = supports_old[:1]
loads = []

for load in loads_old:
    if load.node in nodes:
        loads.append(load)

print(nodes)
print(rods)
print(supports)
print(loads)


def simple_frame_solution(nodes: List[Node], rods: List[Rod], supports: List[Support], loads: List[Force, Momentum]):

    pass

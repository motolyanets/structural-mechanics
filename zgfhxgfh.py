import numpy

from data_base.frames import Node, Rod, Force, DistributedForce
from services.services import round_up

node1 = Node(name='A', x=0, y=0)
node2 = Node(name='2', x=0, y=3.6)
node3 = Node(name='D', x=0, y=7.6)
node4 = Node(name='K', x=9, y=7.6)
node5 = Node(name='5', x=15, y=7.6)
node6 = Node(name='6', x=15, y=3.6)
node7 = Node(name='B', x=15, y=0)
node8 = Node(name='C', x=4.5, y=3.6)

rod1 = Rod(start_node=node1, end_node=node2)
rod2 = Rod(start_node=node2, end_node=node3)
rod3 = Rod(start_node=node3, end_node=node4, stiffness=1.4)
rod4 = Rod(start_node=node4, end_node=node5, stiffness=1.4)
rod5 = Rod(start_node=node5, end_node=node6)
rod6 = Rod(start_node=node6, end_node=node7)
rod7 = Rod(start_node=node2, end_node=node8, stiffness=4)
rod8 = Rod(start_node=node8, end_node=node6, stiffness=4)

load_P = Force(name='P', node=node4, value=13, rotation=270)
load_q = DistributedForce(name='q', rod=rod8, value=2, rotation=270)

nodes = [node1, node2, node3, node4, node5, node6, node7, node8]
rods = [rod1, rod2, rod3, rod4, rod5, rod6, rod7, rod8]
loads = [load_P, load_q]

rod1.diagram_M1 = [0, 1.89]
rod2.diagram_M1 = [1.89, 0]
rod3.diagram_M1 = [0, 0]
rod4.diagram_M1 = [0, 0]
rod5.diagram_M1 = [0, 1.89]
rod6.diagram_M1 = [1.89, 0]
rod7.diagram_M1 = [0, 0]
rod8.diagram_M1 = [0, 0]

rod1.diagram_M2 = [0, 2.13]
rod2.diagram_M2 = [-2.37, 0]
rod3.diagram_M2 = [0, 9]
rod4.diagram_M2 = [9, 15]
rod5.diagram_M2 = [15, 12.63]
rod6.diagram_M2 = [2.13, 0]
rod7.diagram_M2 = [4.5, 0]
rod8.diagram_M2 = [0, -10.5]

rod1.diagram_M3 = [1, 0.53]
rod2.diagram_M3 = [0.53, 0]
rod3.diagram_M3 = [0, -0.6]
rod4.diagram_M3 = [-0.6, -1]
rod5.diagram_M3 = [-1, -0.53]
rod6.diagram_M3 = [-0.53, 0]
rod7.diagram_M3 = [0, 0]
rod8.diagram_M3 = [0, 0]

rod1.diagram_Mp = [0, 0]
rod2.diagram_Mp = [0, 0]
rod3.diagram_Mp = [0, -112.95]
rod4.diagram_Mp = [-112.95, -110.25]
rod5.diagram_Mp = [-110.25, -110.25]
rod6.diagram_Mp = [0, 0]
rod7.diagram_Mp = [0, 0]
rod8.diagram_Mp = [0, 110.25, -2]


def multiply_diagrams_Simpson(rod, diagram_1_name, diagram_2_name):
    diagram_1 = rod.__getattribute__(f'diagram_{diagram_1_name}')
    diagram_2 = rod.__getattribute__(f'diagram_{diagram_2_name}')

    length = rod.length()
    stiffness = rod.stiffness

    multiplied_diagram = []

    d1_start = diagram_1[0]
    d1_center = round_up((diagram_1[0] + diagram_1[1]) / 2, 3)
    d1_end = diagram_1[1]
    d2_start = diagram_2[0]
    d2_center = round_up((diagram_2[0] + diagram_2[1]) / 2, 3)
    d2_end = diagram_2[1]

    if len(diagram_1) == len(diagram_2) == 2:
        result = (length / (6 * stiffness)) * (d1_start * d2_start + 4 * d1_center * d2_center + d1_end * d2_end)
        if result:
            text = (f'({length} / (6 * {stiffness}EI)) * ({d1_start} * {d2_start} + 4 * {round_up(d1_center)} * {round_up(d2_center)} + '
                  f'{d1_end} * {d2_end})')
            multiplied_diagram.append(text)
            multiplied_diagram.append(round_up(result))
    else:
        result = (length / (6 * stiffness)) * (d1_start * d2_start + 4 * d1_center * d2_center + d1_end * d2_end + 4 * d1_center * diagram_2[2] * length**2 / 8)
        if result:
            text =(f'({length} / (6 * {stiffness}EI)) * ({d1_start} * {d2_start} + 4 * {round_up(d1_center)} * {round_up(d2_center)} + '
                  f'{d1_end} * {d2_end} + 4 * {d1_center} * {diagram_2[2]} * {length}^2 / 8)')
            multiplied_diagram.append(text)
            multiplied_diagram.append(round_up(result))


    return multiplied_diagram


def making_report_of_multiply(lst):
    text_1 = ''
    text_2 = ''
    result = 0
    for i in lst:
        if i:
            text_1 += i[0] + ' + '
            text_2 += f'{str(i[1])}/EI' + ' + '
            result += i[1]

    text_2 = text_2.replace("+ -", "- ")
    result = round_up(result)
    text = f'{text_1[:-3]} = {text_2[:-3]} = {result}'

    return text, result


multiply_M1_M1 =[]
multiply_M1_M2 =[]
multiply_M1_M3 =[]
multiply_M2_M2 =[]
multiply_M2_M3 =[]
multiply_M3_M3 =[]
multiply_M1_Mp =[]
multiply_M2_Mp =[]
multiply_M3_Mp =[]

for rod in rods:
    M1_M1 = multiply_diagrams_Simpson(rod, 'M1', 'M1')
    M1_M2 = multiply_diagrams_Simpson(rod, 'M1', 'M2')
    M1_M3 = multiply_diagrams_Simpson(rod, 'M1', 'M3')
    M2_M2 = multiply_diagrams_Simpson(rod, 'M2', 'M2')
    M2_M3 = multiply_diagrams_Simpson(rod, 'M2', 'M3')
    M3_M3 = multiply_diagrams_Simpson(rod, 'M3', 'M3')
    M1_Mp = multiply_diagrams_Simpson(rod, 'M1', 'Mp')
    M2_Mp = multiply_diagrams_Simpson(rod, 'M2', 'Mp')
    M3_Mp = multiply_diagrams_Simpson(rod, 'M3', 'Mp')

    multiply_M1_M1.append(M1_M1)
    multiply_M1_M2.append(M1_M2)
    multiply_M1_M3.append(M1_M3)
    multiply_M2_M2.append(M2_M2)
    multiply_M2_M3.append(M2_M3)
    multiply_M3_M3.append(M3_M3)
    multiply_M1_Mp.append(M1_Mp)
    multiply_M2_Mp.append(M2_Mp)
    multiply_M3_Mp.append(M3_Mp)



delta_11_text, delta_11 = making_report_of_multiply(multiply_M1_M1)
delta_12_text, delta_12 = making_report_of_multiply(multiply_M1_M2)
delta_13_text, delta_13 = making_report_of_multiply(multiply_M1_M3)
delta_22_text, delta_22 = making_report_of_multiply(multiply_M2_M2)
delta_23_text, delta_23 = making_report_of_multiply(multiply_M2_M3)
delta_33_text, delta_33 = making_report_of_multiply(multiply_M3_M3)
delta_1p_text, delta_1p = making_report_of_multiply(multiply_M1_Mp)
delta_2p_text, delta_2p = making_report_of_multiply(multiply_M2_Mp)
delta_3p_text, delta_3p = making_report_of_multiply(multiply_M3_Mp)

print("11 ----", delta_11_text)
print("12 ----", delta_12_text)
print("13 ----", delta_13_text)
print("22 ----", delta_22_text)
print("23 ----", delta_23_text)
print("33 ----", delta_33_text)
print("1p ----", delta_1p_text)
print("2p ----", delta_2p_text)
print("3p ----", delta_3p_text)


print('-------"Эпюра Мs"-------')
for rod in rods:
    Ms_1 = rod.diagram_M1[0] + rod.diagram_M2[0] + rod.diagram_M3[0]
    Ms_2 = rod.diagram_M1[1] + rod.diagram_M2[1] + rod.diagram_M3[1]
    rod.diagram_Ms = [round_up(Ms_1, 3), round_up(Ms_2, 3)]
    print(f'стержень {rod.start_node.name}-{rod.end_node.name} ------ {rod.diagram_Ms}')


print('-------Проверка-------')
multiply_Ms_Ms =[]
for rod in rods:
    Ms_Ms = multiply_diagrams_Simpson(rod, 'Ms', 'Ms')
    multiply_Ms_Ms.append(Ms_Ms)

delta_ss_text, delta_ss = making_report_of_multiply(multiply_Ms_Ms)
print("ss ----", delta_ss_text)
sum_delta = delta_11 + delta_12 * 2 + delta_13 * 2 + delta_22 + delta_23 * 2 + delta_33
print(delta_ss)
print(f'{delta_11} + {delta_12} * 2 + {delta_13} * 2 + {delta_22} + {delta_23} * 2 + {delta_33} = {sum_delta}')
print(sum_delta)
E = (max(delta_ss, sum_delta) - min(delta_ss, sum_delta)) / min(delta_ss, sum_delta) * 100
print(E)

print('-------Проверка-------')
multiply_Ms_Mp =[]
for rod in rods:
    Ms_Mp = multiply_diagrams_Simpson(rod, 'Ms', 'Mp')
    multiply_Ms_Mp.append(Ms_Mp)

delta_sp_text, delta_sp = making_report_of_multiply(multiply_Ms_Mp)
print("sp ----", delta_sp_text)
sum_delta = delta_1p + delta_2p + delta_3p
print(delta_sp)
print(f'{delta_1p} + {delta_2p} + {delta_3p} = {sum_delta}')
print(sum_delta)
E = (max(delta_sp, sum_delta) - min(delta_sp, sum_delta)) / min(delta_sp, sum_delta) * 100
print(E)


print('-------Решение системы уравнений-------')
print(f'delta_11 = {delta_11}')
print(f'delta_12 = {delta_12}')
print(f'delta_13 = {delta_13}')
print(f'delta_22 = {delta_22}')
print(f'delta_23 = {delta_23}')
print(f'delta_33 = {delta_33}')
print(f'delta_1p = {delta_1p}')
print(f'delta_2p = {delta_2p}')
print(f'delta_3p = {delta_3p}')
# Матрица коэффициентов
A = numpy.array([[delta_11, delta_12, delta_13],
                 [delta_12, delta_22, delta_23],
                 [delta_13, delta_23, delta_33]])

# Вектор правых частей
B = numpy.array([-delta_1p, -delta_2p, -delta_3p])

# Решение
solution = numpy.linalg.solve(A, B)
x1 = round_up(solution[0], 3)
x2 = round_up(solution[1], 3)
x3 = round_up(solution[2], 3)
print(f"x1 = {x1}, x2 = {x2}, x3 = {x3}")

print('-------"Эпюра Мок"-------')
for rod in rods:
    Mok_1 = rod.diagram_M1[0]  * x1 + rod.diagram_M2[0] * x2 + rod.diagram_M3[0] * x3 + rod.diagram_Mp[0]
    Mok_2 = rod.diagram_M1[1]  * x1 + rod.diagram_M2[1] * x2 + rod.diagram_M3[1] * x3 + rod.diagram_Mp[1]
    rod.diagram_Mok = [round_up(Mok_1), round_up(Mok_2)]
    print(f'стержень {rod.start_node.name}-{rod.end_node.name} ------ {rod.diagram_Mok}')

rod8.diagram_Mok.append(-2)

print('-------Деформационная проверка-------')
multiply_Ms_Mok =[]
for rod in rods:
    Ms_Mok = multiply_diagrams_Simpson(rod, 'Ms', 'Mok')
    multiply_Ms_Mok.append(Ms_Mok)

minus_results = 0
plus_results = 0

for m in multiply_Ms_Mok:
    if m[1] > 0:
        plus_results += m[1]
    else:
        minus_results += m[1]

delta_sok_text, delta_sok = making_report_of_multiply(multiply_Ms_Mok)
print("sok ----", delta_sok_text)
E = (minus_results + plus_results) / min(abs(minus_results), plus_results) * 100
print(f'({minus_results} + {plus_results}) / {min(abs(minus_results), plus_results)} * 100 = {E}')

print('-------"Эпюра Q"-------')
for rod in rods:
    if len(rod.diagram_Mok) == 2:
        Q = (rod.diagram_Mok[0] - rod.diagram_Mok[1]) / rod.length()
        rod.diagram_Q = [round_up(Q), round_up(Q)]
    else:
        rod.diagram_Q = []
    print(f'стержень {rod.start_node.name}-{rod.end_node.name} ------ {rod.diagram_Q}')


print('-------"Перемещение в т.К"-------')
rod1.diagram_Mk = [0, 0]
rod2.diagram_Mk = [0, 0]
rod3.diagram_Mk = [0, -3.6]
rod4.diagram_Mk = [-3.6, 0]
rod5.diagram_Mk = [0, 0]
rod6.diagram_Mk = [0, 0]
rod7.diagram_Mk = [0, 0]
rod8.diagram_Mk = [0, 0]

multiply_Mk_Mok =[]
for rod in rods:
    Mk_Mok = multiply_diagrams_Simpson(rod, 'Mk', 'Mok')
    multiply_Mk_Mok.append(Mk_Mok)

delta_kok_text, delta_kok = making_report_of_multiply(multiply_Mk_Mok)
print("kok ----", delta_kok_text)

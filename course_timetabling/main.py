import gurobipy as gp
from gurobipy import GRB

from utils import get_disciplinas_dias_horarios, professor_apto, get_carga_horaria, get_disciplinas_a_partir_de_um_dia, get_disciplinas_a_partir_de_um_horario
import input

m = gp.Model("CourseTimetabling")

P = input.professores
D = input.disciplinas
DISCIPLINA_DIAS, DISCILINA_HORARIOS = get_disciplinas_dias_horarios(D)


# =================================== 
#   COEFICIENTES E VARIÁVEIS
# ===================================

f = {} # Coeficientes
X = {} # Variáveis

for p in P:

    f[p] = {}
    X[p] = {}
    disciplinas_aptas = professor_apto(p)

    for d in D.keys():

        f[p][d] = {}
        X[p][d] = {}

        CH = get_carga_horaria(D, d)
        f[p][d][CH[0]] = {}
        f[p][d][CH[0]][CH[1]] = {}

        # {'Adriana Vivacqua': {'ICP131_A': {...}}}
        # {'SEG': {'8:00-10:00': 0}, 'QUA': {'8:00-10:00': 0}}

        if D[d][0] in disciplinas_aptas:
            a = 1 
        else:
            a = 0

        f[p][d][CH[0]][CH[1]] = a

        # Variavel
        X[p][d][CH[0]] = {}
        X[p][d][CH[0]][CH[1]] = {}
        X[p][d][CH[0]][CH[1]] = m.addVar(vtype=GRB.BINARY, name=f"{p}_{d}_{CH[0]}_{CH[1]}")
    pass


# =================================== 
#   FUNÇÃO OBJETIVO
# ===================================

m.setObjective(gp.quicksum((X[p][d][CH[0]][CH[1]] * f[p][d][CH[0]][CH[1]]) for p in P for d in D.keys() for CH in [get_carga_horaria(D,d)]), GRB.MAXIMIZE)


# =================================== 
#   RESTRIÇÕES
# ===================================

# Restrições de créditos por professor
for p in P:
    # RH1: Regime de trabalho (quantidade de horas) - quantidade de créditos mínimo
    m.addConstr(gp.quicksum([X[p][d][get_carga_horaria(D,d)[0]][get_carga_horaria(D,d)[1]] * D[d][2] for d in D.keys()]) >= 8)

    # RH2: Regime de trabalho (quantidade de horas) - quantidade de créditos máximo
    m.addConstr(gp.quicksum([X[p][d][get_carga_horaria(D,d)[0]][get_carga_horaria(D,d)[1]] * D[d][2] for d in D.keys()]) <= 8)
    
# RH3: Uma disciplina de uma turma, deverá ser ministrada por um único professor
# TODO: avaliar se é o caso de somente disciplinas obrigatórias
for d in D.keys():
    CH = get_carga_horaria(D,d)
    m.addConstr(gp.quicksum([X[p][d][CH[0]][CH[1]] for p in P]) == 1)


# RH4: Um professor poderá dar no máximo 1 disciplina de uma turma em um mesmo dia e horário (binário OU <= 1)

for p in P:
    print(DISCIPLINA_DIAS)
    print(DISCILINA_HORARIOS)
    for i in range(len(DISCIPLINA_DIAS)):
        A = get_disciplinas_a_partir_de_um_dia(D,DISCIPLINA_DIAS[i])            
        B = get_disciplinas_a_partir_de_um_horario(D, DISCILINA_HORARIOS[i])
        C = A.intersection(B)
        print(DISCIPLINA_DIAS[i], DISCILINA_HORARIOS[i])
        print(A,B,C)

        dias = DISCIPLINA_DIAS[i].split(",")
        m.addConstr(gp.quicksum([X[p][d][get_carga_horaria(D,d)[0]][get_carga_horaria(D,d)[1]] for d in C]) <= 1)

# TODO: não deixar que um professor sem ser de uma área ministre uma disciplina. Ex.: Daniel Sadoc_ICP370_TER,QUI_8:00-10:00 1
# TODO: adicionar professor dummy para que ele seja alocado caso não tenha professor disponível



m.update()
m.optimize()

for v in m.getVars():
    print('%s %g' % (v.VarName, v.X))

print('Obj: %g' % m.ObjVal)

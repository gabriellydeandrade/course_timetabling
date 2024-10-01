import gurobipy as gp
from gurobipy import GRB

import course_timetabling.utils.utils as utils
import input

m = gp.Model("CourseTimetabling")

P = input.professores
PP = input.professores_permanentes
PS = input.professores_substitutos
D = input.disciplinas
DISCIPLINA_DIAS, DISCILINA_HORARIOS = utils.get_disciplinas_dias_horarios(D)

DUMMY_PROFESSOR = "DUMMY" 
DUMMY_COEFFICIENT = 0.0001


# ===================================
#   COEFICIENTES E VARIÁVEIS
# ===================================


f = {}  # Coeficientes
X = {}  # Variáveis

for p in P:

    f[p] = {}
    X[p] = {}
    disciplinas_aptas = utils.professor_apto(p)

    for d in D.keys():

        f[p][d] = {}
        X[p][d] = {}

        CH = utils.get_carga_horaria(D, d)
        f[p][d][CH[0]] = {}
        f[p][d][CH[0]][CH[1]] = {}

        if p == DUMMY_PROFESSOR:
            a = DUMMY_COEFFICIENT
        elif d in disciplinas_aptas:
            a = 1
        else:
            a = 0

        f[p][d][CH[0]][CH[1]] = a

        # Variavel
        X[p][d][CH[0]] = {}
        X[p][d][CH[0]][CH[1]] = {}
        X[p][d][CH[0]][CH[1]] = m.addVar(
            vtype=GRB.BINARY, name=f"{p}_{d}_{CH[0]}_{CH[1]}"
        )
    pass

PNC = {} # Variável de folga que indica quantos créditos o professor está abaixo do ideal pela coordenação
for p in PP:
    PNC[p] = {}
    PNC[p] = m.addVar(vtype=GRB.INTEGER, name=f"PNC_{p}")

# ===================================
#   RESTRIÇÕES FRACAS
# ===================================

Wf = 1000
FALpp = 8 # Quantidade mínima de créditos a serem alcançadas pelo professor

# RF1: Garante que o professor seja alocado com a quantidade de créditos sujerida pela coordenação se possível. Não inviabilisa o modelo caso não seja atingido. 

for p in PP:
    m.addConstr(
        gp.quicksum(
            [
                X[p][d][utils.get_carga_horaria(D, d)[0]][utils.get_carga_horaria(D, d)[1]]
                * D[d][2]
                for d in D.keys()
            ]
        )
        == FALpp - PNC[p] #TODO: será que aqui eu coloco igual ou >= ? Nesse caso o professor iria assumir mais disciplinas
    )


# ===================================
#   FUNÇÃO OBJETIVO
# ===================================

m.setObjective(
    expr=gp.quicksum(
        (X[p][d][CH[0]][CH[1]] * f[p][d][CH[0]][CH[1]])
        for p in P
        for d in D.keys()
        for CH in [utils.get_carga_horaria(D, d)]
    )
    - 
    gp.quicksum(Wf * PNC[pp] for pp in PP),
    sense=GRB.MAXIMIZE
)


# ===================================
#   RESTRIÇÕES
# ===================================


# RH2: Regime de trabalho (quantidade de horas) - quantidade de créditos máximo para o professor substituto

FALps = 12 # Quantidade máxima de créditos a serem alcançadas pelo professor substituto
for p in PS:
    m.addConstr(
        gp.quicksum(
            [
                X[p][d][utils.get_carga_horaria(D, d)[0]][utils.get_carga_horaria(D, d)[1]]
                * D[d][2]
                for d in D.keys()
            ]
        )
        <= FALps
    )

# RH3: Uma disciplina de uma turma, deverá ser ministrada por um único professor

for d in D.keys():
    CH = utils.get_carga_horaria(D, d)
    m.addConstr(gp.quicksum([X[p][d][CH[0]][CH[1]] for p in P]) == 1)


# RH4: Um professor poderá dar no máximo 1 disciplina de uma turma em um mesmo dia e horário (binário OU <= 1)

for p in P:
    if p == DUMMY_PROFESSOR:
        continue

    for i in range(len(DISCIPLINA_DIAS)):
        print(DISCIPLINA_DIAS[i], DISCILINA_HORARIOS[i])
        A = utils.get_disciplinas_a_partir_de_um_dia(D, DISCIPLINA_DIAS[i])
        B = utils.get_disciplinas_a_partir_de_um_horario(D, DISCILINA_HORARIOS[i])
        C = A.intersection(B)

        m.addConstr(
            gp.quicksum(
                [
                    X[p][d][utils.get_carga_horaria(D, d)[0]][utils.get_carga_horaria(D, d)[1]]
                    for d in C
                ]
            )
            <= 1
        )


# RH5: Um professor não pode lecionar uma disciplina em que ele não esteja apto

for p in P:
    todas_disciplinas = utils.get_codigo_disciplinas(D)
    disciplinas_aptas = utils.professor_apto(p)

    disciplinas_nao_aptas = todas_disciplinas.difference(disciplinas_aptas)

    m.addConstr(
        gp.quicksum(
            [
                X[p][d][utils.get_carga_horaria(D, d)[0]][utils.get_carga_horaria(D, d)[1]]
                for d in disciplinas_nao_aptas
            ]
        )
        == 0
    )


m.update()
m.optimize()

print("========= RESULT ==========")

for v in m.getVars():
    if v.X > 0:
        print("%s %g" % (v.VarName, v.X))

print("=============================")

print("Obj: %g" % m.ObjVal)

import gurobipy as gp
from gurobipy import GRB

import input


m = gp.Model("CourseTimetabling")


P = input.professores
D = input.disciplinas
S = input.dia_semana
H = input.horarios
PROFESSOR_APTO = input.professores_area_conhecimento
AREAS_CONHECIMENTO = input.areas_conhecimento
HORARIOS = input.horarios

def get_carga_horaria():
    pass


f = {} # Coeficientes
X = {} # Variáveis

for p in P:

    f[p] = {}
    X[p] = {}

    for d in D.keys():

        f[p][d] = {}
        X[p][d] = {}

        for CH in D[d][1]: # pega carga horária
            f[p][d][CH[0]] = {}
            f[p][d][CH[0]][CH[1]] = {}

            # {'Adriana Vivacqua': {'ICP131_A': {...}}}
            # {'SEG': {'8:00-10:00': 0}, 'QUA': {'8:00-10:00': 0}}

            # Verificação se o professor está apto a ministrar a disciplina
            try:
                areas_professor = PROFESSOR_APTO[p]
            except KeyError:
                print(f"====Professor {p} não encontrado na lista de perfil de disciplinas")
            disciplinas_aptas = []
            for area in areas_professor:
                disciplinas_aptas.append(AREAS_CONHECIMENTO[area])

            if D[d][0] in disciplinas_aptas:
                a = 1 
            else:
                a = 0

            f[p][d][CH[0]][CH[1]] = a

            # Variavel
            X[p][d][CH[0]] = {}
            X[p][d][CH[0]][CH[1]] = {}
            X[p][d][CH[0]][CH[1]] = m.addVar(vtype=GRB.BINARY, name=f"{p}_{d}_{CH[0]}_{CH[1]}")


# Restrições

# Fixado uma disciplina de uma turma, só poderemos ter um professor alocado

# for d in D.keys():
#     for CH in D[d][1]: # pega carga horária
#         m.addConstr(sum([X[p][d][CH[0]][CH[1]] for p in P]) == 1)

# Fixado um professor, esse só pode dar aula em um único dia e horário

# def get_disciplinas_a_partir_de_um_horario(disciplinas: dict, horario:str):
#     keys = []
#     for disciplina,detalhe in disciplinas.items():
#         if detalhe[1] == horario:
#             keys.append(disciplina)
#     return keys

# def get_disciplinas_a_partir_de_um_dia(disciplinas: dict, dia:str):
#     keys = []
#     for disciplina,detalhe in disciplinas.items():
#         if detalhe[0] == dia:
#             keys.append(disciplina)
#     return keys

# for p in P:
#     for s in S:
#         A = get_disciplinas_a_partir_de_um_dia(D, s)
#         for h in H:
#             B = get_disciplinas_a_partir_de_um_horario(D, h)
#             C = set(A).intersection(B)
#             m.addConstr(sum([X[p][d][s][h] for d in C]) <= 1)

# Restrições de créditos por professor
# for p in P:
#     for d in D.keys():
#         for CH in D[d][1]: # pega carga horária
#             m.addConstr(sum([X[p][d][CH[0]][CH[1]] * D[d][2]]) >= 8)
#             # m.addConstr(sum([X[p][d][CH[0]][CH[1]] * D[d][2]]) <= 12)
    
#     print('hey')



# Função objetivo

m.setObjective(sum((X[p][d][CH[0]][CH[1]] * f[p][d][CH[0]][CH[1]]) for p in P for d in D.keys() for CH in D[d][1]), GRB.MAXIMIZE)

m.update()
m.optimize()

for v in m.getVars():
    print('%s %g' % (v.VarName, v.X))

print('Obj: %g' % m.ObjVal)

import gurobipy as gp
from gurobipy import GRB

from utils import all_equal
import input

m = gp.Model("CourseTimetabling")

P = input.professores
D = input.disciplinas
DISCIPLINA_DIAS = input.disciplinas_dias
DISCILINA_HORARIOS = input.disciplinas_horarios
PROFESSOR_APTO = input.professores_area_conhecimento
AREAS_CONHECIMENTO = input.areas_conhecimento

def get_carga_horaria(disciplina):
    # Retorna um horário se todos forem iguais
    carga_horaria = D[disciplina][1]

    dias = []
    horas = []

    for ch in carga_horaria:
        dias.append(ch[0])
        horas.append(ch[1])

    if all_equal(dias):
        dias = [dias[0]]
    if all_equal(horas):
        horas = [horas[0]]
    
    dia = ','.join(dias)
    hora = ','.join(horas)
    return dia,hora


f = {} # Coeficientes
X = {} # Variáveis

def professor_apto(p):
    # Verificação se o professor está apto a ministrar a disciplina
    try:
        areas_professor = PROFESSOR_APTO[p]
    except KeyError:
        print(f"====Professor {p} não encontrado na lista de perfil de disciplinas")
    disciplinas_aptas = []
    for area in areas_professor:
        disciplinas_aptas = disciplinas_aptas + AREAS_CONHECIMENTO[area]

    result = set(disciplinas_aptas)
    return result

for p in P:

    f[p] = {}
    X[p] = {}
    disciplinas_aptas = professor_apto(p)

    for d in D.keys():

        f[p][d] = {}
        X[p][d] = {}

        CH = get_carga_horaria(d)
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


# Restrições

def get_disciplinas_a_partir_de_um_horario(disciplinas: dict, horario:str):
    keys = []
    for disciplina,detalhe in disciplinas.items():
         for carga_horaria in detalhe[1]:
            if carga_horaria[1] in horario:
                keys.append(disciplina)
    result = set(keys)
    return result

def get_disciplinas_a_partir_de_um_dia(disciplinas: dict, dia:str):
    keys = []
    for disciplina,detalhe in disciplinas.items():
        for carga_horaria in detalhe[1]:
            if carga_horaria[0] in dia:
                keys.append(disciplina)
    result = set(keys)
    return result

for d in D.keys():
    CH = get_carga_horaria(d)
    m.addConstr(gp.quicksum([X[p][d][CH[0]][CH[1]] for p in P]) == 1)

# Fixado um professor, esse só pode dar aula em um único dia e horário

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
        m.addConstr(gp.quicksum([X[p][d][get_carga_horaria(d)[0]][get_carga_horaria(d)[1]] for d in C]) <= 1)

# TODO: não deixar que um professor sem ser de uma área ministre uma disciplina. Ex.: Daniel Sadoc_ICP370_TER,QUI_8:00-10:00 1
# TODO: adicionar professor dummy para que ele seja alocado caso não tenha professor disponível

# Restrições de créditos por professor
for p in P:
    m.addConstr(gp.quicksum([X[p][d][get_carga_horaria(d)[0]][get_carga_horaria(d)[1]] * D[d][2] for d in D.keys()]) >= 8)
    m.addConstr(gp.quicksum([X[p][d][get_carga_horaria(d)[0]][get_carga_horaria(d)[1]] * D[d][2] for d in D.keys()]) <= 8)
    

# Função objetivo

m.setObjective(gp.quicksum((X[p][d][CH[0]][CH[1]] * f[p][d][CH[0]][CH[1]]) for p in P for d in D.keys() for CH in [get_carga_horaria(d)]), GRB.MAXIMIZE)

m.update()
m.optimize()

for v in m.getVars():
    print('%s %g' % (v.VarName, v.X))

print('Obj: %g' % m.ObjVal)

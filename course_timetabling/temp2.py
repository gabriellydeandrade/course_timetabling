from gurobipy import Model, GRB

# Inicializando o modelo
m = Model("Scheduling")

# Função de satisfação
f = {}
X = {}
Y = {}

V= [('SEG', '8:00-10:00'), ('QUA', '8:00-10:00')]

 Definição de dicionário D com um trecho de exemplo
D = {
    'IC239T02': ['IC239', '8:00-10:00', 'TER,QUI', 4],
    'IC239T03': ['IC239', '13:00-15:00', 'TER,QUI', 4],
    'IC239T04': ['IC239', '15:00-17:00', 'TER,QUI', 4],
    'IC239T64': ['IC239', '18:00-20:00', 'QUA,SEX', 4],
    'IC241T01': ['IC239', '10:00-12:00', 'SEG,QUA,SEX', 6],
    # Exemplo de mais entradas:
    'IC241T02': ['IC241', '8:00-10:00', 'SEG,QUA,SEX', 6],
    'IC241T03': ['IC241', '15:00-17:00', 'SEG,QUA,SEX', 6],
    'IC241T04': ['IC241', '13:00-15:00', 'SEG,QUA,SEX', 6]
}

# Conjunto de dias
S = ['SEG,QUA', 'TER,QUI', 'SEG,QUA,SEX', 'QUA,SEX']

# Conjunto de intervalos de tempo
H = ['8:00-10:00', '10:00-12:00', '13:00-15:00', '15:00-17:00', '18:00-20:00', '20:00-22:00']

# Conjunto de professores
P = [
    'ALINE', 'ANDRÉMARTINS', 'ANDRÉSMAURÍCIO', 'ANGEL', 'CARLOSANDRÉS',
    'CLÁUDIO', 'DANIEL', 'DOUGLAS', 'DUILIO', 'EDIVALDO'
]

# Preferências de disciplinas dos professores
PrefD = {
    'ALINE': ['IC243', 'IC251', 'IC260', 'IC270', 'IC815'],
    'ANDRÉMARTINS': ['IC260', 'IC267', 'IC269', 'IC276', 'IC862', 'IC863'],
    'ANDRÉSMAURÍCIO': ['IC243', 'IC260', 'IC270', 'IC855'],
    'ANGEL': ['IC251', 'IC252', 'IC278'],
    'CARLOSANDRÉS': ['IC243', 'IC244', 'IC297'],
    # Mais entradas aqui...
}

# Preferências de turnos dos professores
PrefT = {
    'ALINE': ['8:00-10:00', '10:00-12:00', '13:00-15:00', '15:00-17:00'],
    'ANDRÉMARTINS': ['8:00-10:00', '10:00-12:00', '13:00-15:00', '15:00-17:00'],
    'ANDRÉSMAURÍCIO': ['18:00-20:00', '20:00-22:00'],
    # Mais entradas aqui...
}

# Função para obter chaves por valores
def getKeysByValues(dictOfElements, listOfValues):
    listOfKeys = []
    listOfItems = dictOfElements.items()
    for item in listOfItems:
        if item[1][2] == listOfValues:
            listOfKeys.append(item[0])
    return listOfKeys

for p in P:
    f[p] = {}
    for d in D.keys():
        f[p][d] = {}
        f[p][d][D[d][2]] = {}
        f[p][d][D[d][2]][D[d][1]] = {}

        # Verificação de preferências de áreas
        SB = set(PrefA.get(p))
        a = 1 if D[d][0] in SB else 0

        # Verificação de preferências de disciplinas
        SD = set(PrefD.get(p))
        k = 73 if D[d][0] in SD else 0

        # Verificação de preferências de turnos
        ST = set(PrefT.get(p))
        w = 27 if D[d][1] in ST else 0

        # Calculando a função de satisfação
        f[p][d][D[d][2]][D[d][1]] = a * (k + w)

# Definição das variáveis binárias e função objetivo
for p in P:
    X[p] = {}
    for d in D.keys():
        X[p][d] = {}
        X[p][d][D[d][2]] = {}
        X[p][d][D[d][2]][D[d][1]] = m.addVar(vtype=GRB.BINARY, 
                                             name="%s_%s_%s_%s" % (p, d, D[d][2], D[d][1]))

for p in P:
    Y[p] = m.addVar(vtype=GRB.BINARY, name="%s" % p)

# Função objetivo
m.setObjective(quicksum((X[p][d][D[d][2]][D[d][1]] * f[p][d][D[d][2]][D[d][1]]) 
                        for p in P for d in D.keys()), GRB.MAXIMIZE)

# Atualizando o modelo
m.update()

# Restrições
# Apenas um professor pode ser alocado
m.addConstr(quicksum(Y[p] for p in P) <= 1)

# Restrições fracas: alocar professor apenas em sua área de competência
for p in P:
    for d in D.keys():
        SB = set(PrefA.get(p))
        if D[d][0] not in SB:
            m.addConstr(X[p][d][D[d][2]][D[d][1]] <= Y[p])

# Restrições fortes
# Exemplo de restrições sobre dias e horários incompatíveis
for p in P:
    for d in W:
        for t in T:
            m.addConstr((X[p][d][D[W[0]][2]][D[d][1]]) +
                        (X[p][t][D[T[6]][2]][D[t][1]]) <= 1)

# Outras restrições para dias e horários
for p in P:
    for d in Z:
        for t in T:
            m.addConstr((X[p][d][D[Z[0]][2]][D[d][1]]) +
                        (X[p][t][D[T[6]][2]][D[t][1]]) <= 1)

# Um professor só pode dar uma aula em um horário por dia
for p in P:
    for s in S:
        for h in H:
            A = getKeysByValues4(D, h)
            B = getKeysByValues3(D, s)
            C = set(A).intersection(B)
            m.addConstr(quicksum([X[p][d][s][h] for d in C]) <= 1)

# Uma disciplina só pode ser dada por um professor
for d in D.keys():
    m.addConstr(quicksum([X[p][d][D[d][2]][D[d][1]] for p in P]) == 1)

# Exemplo de restrições de alocação de horários
for p in P:
    for h in H:
        A = getKeysByValues4(D, h)
        B = set(A).intersection(I)
        C = set(A).intersection(Z)
        for d in C:
            for z in B:
                m.addConstr((X[p][z][D[I[0]][2]][h]) +
                            (X[p][d][D[Z[0]][2]][h]) <= 1)

# Restrições de créditos por professor
for p in P:
    m.addConstr(quicksum([X[p][d][D[d][2]][D[d][1]] * D[d][3] for d in D.keys()]) >= 8)
    m.addConstr(quicksum([X[p][d][D[d][2]][D[d][1]] * D[d][3] for d in D.keys()]) <= 12)

# Otimizar o modelo
m.optimize()

# Mostrar as variáveis de decisão ativas
for v in m.getVars():
    if v.x == 1:
        print(v.varName, v.x)

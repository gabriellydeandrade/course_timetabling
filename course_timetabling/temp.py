# Definição de dicionário D com um trecho de exemplo
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

# Função principal de agendamento
def main():
    # Exemplo de uso
    keys_seg_qua = getKeysByValues(D, 'TER,QUI')
    print("Aulas nos dias SEG e QUA:", keys_seg_qua)

if __name__ == "__main__":
    main()

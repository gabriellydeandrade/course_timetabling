from itertools import groupby, islice, product
import input


PROFESSOR_AREA_APTO = input.professores_area_conhecimento
AREAS_CONHECIMENTO = input.areas_conhecimento

def professor_apto(p):
    # Verificação se o professor está apto a ministrar a disciplina
    try:
        areas_professor = PROFESSOR_AREA_APTO[p]
    except KeyError:
        print(f"====Professor {p} não encontrado na lista de perfil de disciplinas")
    disciplinas_aptas = []
    for area in areas_professor:
        disciplinas_aptas = disciplinas_aptas + AREAS_CONHECIMENTO[area]

    result = set(disciplinas_aptas)
    return result

def get_disciplinas_dias_horarios(disciplinas: dict): 
    disciplinas_dias = []
    disciplinas_horarios = []

    for _,detalhe in disciplinas.items():
        dias = []
        horarios = []
        for x in detalhe[1]:
            dias.append(x[0])

        for x in detalhe[1]:
            horarios.append(x[1])

        if all_equal(dias):
            dias = [dias[0]]
        if all_equal(horarios):
            horarios = [horarios[0]]

        dia = ','.join(dias)
        hora = ','.join(horarios)
        disciplinas_dias.append(dia)
        disciplinas_horarios.append(hora)
    return disciplinas_dias, disciplinas_horarios

def get_carga_horaria(D, disciplina):
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

def take(n, iterable):
    "Return first n items of the iterable as a list."
    return list(islice(iterable, n))

def all_equal(iterable, key=None):
    "Returns True if all the elements are equal to each other."
    return len(take(2, groupby(iterable, key))) <= 1

# print(all_equal([1,2]))

def cartesian(iterable):
    elements = []
    for elem in product(*iterable):
        if len(elem[0].split(",")) < len(elem[1].split(",")):
            continue
        elements.append(elem)
    return elements


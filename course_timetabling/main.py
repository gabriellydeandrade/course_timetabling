import gurobipy as gp
from gurobipy import GRB

import utils.utils as utils
import input
from database.input_global_sets import courses_set
from database.construct_sets import get_course_schedule

# Constants
DUMMY_PROFESSOR = "DUMMY"
DUMMY_COEFFICIENT = 0.0001
DEFAULT_COEFFICIENT = 1
ZERO_COEFFICIENT = 0
WEIGHT_FACTOR = 1000
MIN_CREDITS_PERMANENT = 8
MAX_CREDITS_SUBSTITUTE = 12

# Initialize model
model = gp.Model("CourseTimetabling")

# Input data
professors = input.professores
permanent_professors = input.professores_permanentes
substitute_professors = input.professores_substitutos
COURSES = courses_set
course_days, course_times = utils.get_disciplinas_dias_horarios(COURSES)

# Coefficients and variables
coefficients = {}
variables = {}


def initialize_variables_and_coefficients():
    for professor in professors:
        coefficients[professor] = {}
        variables[professor] = {}
        qualified_courses = utils.professor_apto(professor)

        for course in COURSES.keys():
            coefficients[professor][course] = {}
            variables[professor][course] = {}

            workload = get_course_schedule(COURSES, course)
            day, time = workload

            coefficients[professor][course][day] = {}
            coefficients[professor][course][day][time] = (
                DUMMY_COEFFICIENT
                if professor == DUMMY_PROFESSOR
                else (
                    DEFAULT_COEFFICIENT
                    if course in qualified_courses
                    else ZERO_COEFFICIENT
                )
            )

            variables[professor][course][day] = {}
            variables[professor][course][day][time] = model.addVar(
                vtype=GRB.BINARY, name=f"{professor}_{course}_{day}_{time}"
            )


def add_credit_slack_variables():
    # Variável de folga que indica quantos créditos o professor está abaixo do ideal pela coordenação
    slack_variables = {}
    for professor in permanent_professors:
        slack_variables[professor] = model.addVar(
            vtype=GRB.INTEGER, name=f"PNC_{professor}"
        )
    return slack_variables


def add_constraints(slack_variables):
    # Soft constraints
    # RF1: Garante que o professor seja alocado com a quantidade de créditos sujerida pela coordenação se possível. Não inviabilisa o modelo caso não seja atingido.

    for professor in permanent_professors:
        model.addConstr(
            gp.quicksum(
                variables[professor][course][get_course_schedule(COURSES, course)[0]][
                    get_course_schedule(COURSES, course)[1]
                ]
                * COURSES[course][2]
                for course in COURSES.keys()
            )
            == MIN_CREDITS_PERMANENT - slack_variables[professor]
        )

    # Hard constraints
    # RH2: Regime de trabalho (quantidade de horas) - quantidade de créditos máximo para o professor substituto

    for professor in substitute_professors:
        model.addConstr(
            gp.quicksum(
                variables[professor][course][get_course_schedule(COURSES, course)[0]][
                    get_course_schedule(COURSES, course)[1]
                ]
                * COURSES[course][2]
                for course in COURSES.keys()
            )
            <= MAX_CREDITS_SUBSTITUTE
        )

    # RH3: Uma disciplina de uma turma, deverá ser ministrada por um único professor
    for course in COURSES.keys():
        workload = get_course_schedule(COURSES, course)
        day, time = workload
        model.addConstr(
            gp.quicksum(
                variables[professor][course][day][time] for professor in professors
            )
            == 1
        )

    # RH4: Um professor poderá dar no máximo 1 disciplina de uma turma em um mesmo dia e horário (binário OU <= 1)
    for professor in professors:
        if professor == DUMMY_PROFESSOR:
            continue
        for i in range(len(course_days)):
            day = course_days[i]
            time = course_times[i]
            day_courses = utils.get_disciplinas_a_partir_de_um_dia(COURSES, day)
            time_courses = utils.get_disciplinas_a_partir_de_um_horario(COURSES, time)
            common_courses = day_courses.intersection(time_courses)
            model.addConstr(
                gp.quicksum(
                    variables[professor][course][
                        get_course_schedule(COURSES, course)[0]
                    ][get_course_schedule(COURSES, course)[1]]
                    for course in common_courses
                )
                <= 1
            )

    # RH5: Um professor não pode lecionar uma disciplina em que ele não esteja apto
    for professor in professors:
        all_courses = utils.get_codigo_disciplinas(COURSES)
        qualified_courses = utils.professor_apto(professor)
        unqualified_courses = all_courses.difference(qualified_courses)
        model.addConstr(
            gp.quicksum(
                variables[professor][course][get_course_schedule(COURSES, course)[0]][
                    get_course_schedule(COURSES, course)[1]
                ]
                for course in unqualified_courses
            )
            == 0
        )


def set_objective(slack_variables):
    model.setObjective(
        gp.quicksum(
            variables[professor][course][day][time]
            * coefficients[professor][course][day][time]
            for professor in professors
            for course in COURSES.keys()
            for day, time in [get_course_schedule(COURSES, course)]
        )
        - gp.quicksum(
            WEIGHT_FACTOR * slack_variables[professor]
            for professor in permanent_professors
        ),
        GRB.MAXIMIZE,
    )


def init_model():
    initialize_variables_and_coefficients()
    slack_variables = add_credit_slack_variables()
    add_constraints(slack_variables)
    set_objective(slack_variables)
    model.update()
    model.optimize()

    professor_timeschedule = []
    for var in model.getVars():
        if var.X > 0:
            professor_timeschedule.append(f"{var.VarName} {var.X}")

    model_value = model.ObjVal
    return professor_timeschedule, model_value


if __name__ == "__main__":
    professor_timeschedule, model_value = init_model()
    print("========= RESULT ==========")
    for r in professor_timeschedule:
        print(r)
    print("=============================")
    print(f"Obj: {model_value}")

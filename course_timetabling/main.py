import gurobipy as gp
from gurobipy import GRB

from utils import utils
from database.construct_sets import get_courses_set, get_professors_set


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

# Coefficients and variables
coefficients = {}
variables = {}


def initialize_variables_and_coefficients():
    for professor in PROFESSORS:
        coefficients[professor] = {}
        variables[professor] = {}
        qualified_courses = utils.get_qualified_courses_for_professor(COURSES, PROFESSORS, professor)

        for course in COURSES.keys():
            coefficients[professor][course] = {}
            variables[professor][course] = {}

            workload = utils.get_course_schedule(COURSES, course)
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
    for professor in PERMANENT_PROFESSORS:
        slack_variables[professor] = model.addVar(
            vtype=GRB.INTEGER, name=f"PNC_{professor}"
        )
    return slack_variables


def add_constraints(slack_variables):
    # Soft constraints
    # RF1: Garante que o professor seja alocado com a quantidade de créditos sujerida pela coordenação se possível. Não inviabilisa o modelo caso não seja atingido.

    for professor in PERMANENT_PROFESSORS:
        model.addConstr(
            gp.quicksum(
                variables[professor][course][utils.get_course_schedule(COURSES, course)[0]][
                    utils.get_course_schedule(COURSES, course)[1]
                ]
                * COURSES[course]['credits']
                for course in COURSES.keys()
            )
            == MIN_CREDITS_PERMANENT - slack_variables[professor]
        )

    # Hard constraints
    # RH2: Regime de trabalho (quantidade de horas) - quantidade de créditos máximo para o professor substituto

    for professor in SUBSTITUTE_PROFESSORS:
        model.addConstr(
            gp.quicksum(
                variables[professor][course][utils.get_course_schedule(COURSES, course)[0]][
                    utils.get_course_schedule(COURSES, course)[1]
                ]
                * COURSES[course]['credits']
                for course in COURSES.keys()
            )
            <= MAX_CREDITS_SUBSTITUTE
        )

    # RH3: Uma disciplina de uma turma, deverá ser ministrada por um único professor
    for course in COURSES.keys():
        workload = utils.get_course_schedule(COURSES, course)
        day, time = workload
        model.addConstr(
            gp.quicksum(
                variables[professor][course][day][time] for professor in PROFESSORS
            )
            == 1
        )

    # RH4: Um professor poderá dar no máximo 1 disciplina de uma turma em um mesmo dia e horário (binário OU <= 1)
    for professor in PROFESSORS:
        if professor == DUMMY_PROFESSOR:
            continue
        for i in range(len(course_days)):
            day = course_days[i]
            time = course_times[i]
            day_courses = utils.get_courses_by_day(COURSES, day)
            time_courses = utils.get_courses_by_time(COURSES, time)
            common_courses = day_courses.intersection(time_courses)
            model.addConstr(
                gp.quicksum(
                    variables[professor][course][
                        utils.get_course_schedule(COURSES, course)[0]
                    ][utils.get_course_schedule(COURSES, course)[1]]
                    for course in common_courses
                )
                <= 1
            )

    # RH5: Um professor não pode lecionar uma disciplina em que ele não esteja apto
    for professor in PROFESSORS:
        all_courses = utils.get_all_course_class_id(COURSES)
        qualified_courses = utils.get_qualified_courses_for_professor(COURSES, PROFESSORS, professor)
        unqualified_courses = all_courses.difference(qualified_courses)
        model.addConstr(
            gp.quicksum(
                variables[professor][course][utils.get_course_schedule(COURSES, course)[0]][
                    utils.get_course_schedule(COURSES, course)[1]
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
            for professor in PROFESSORS
            for course in COURSES.keys()
            for day, time in [utils.get_course_schedule(COURSES, course)]
        )
        - gp.quicksum(
            WEIGHT_FACTOR * slack_variables[professor]
            for professor in PERMANENT_PROFESSORS
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
    COURSES = get_courses_set()
    course_days, course_times = utils.get_possible_schedules(COURSES)

    professors_permanent_set, professors_substitute_set = get_professors_set()
    professors_set = professors_permanent_set | professors_substitute_set
    PROFESSORS = professors_set
    PERMANENT_PROFESSORS = professors_permanent_set
    SUBSTITUTE_PROFESSORS = professors_substitute_set

    professor_timeschedule, model_value = init_model()
    print("========= RESULT ==========")
    for r in professor_timeschedule:
        print(r)
    print("=============================")
    print(f"Obj: {model_value}")

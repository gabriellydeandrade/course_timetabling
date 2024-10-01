import gurobipy as gp
from gurobipy import GRB
import course_timetabling.utils.utils as utils
import input

"""
Course Timetabling Optimization using Gurobi

This script sets up and solves a course timetabling problem using the Gurobi optimization library. 
The goal is to allocate professors to courses in a way that satisfies various constraints and maximizes 
a given objective function.

Modules:
    gurobipy: Gurobi Python interface
    utils: Custom utility functions for the problem
    input: Input data for the problem

Variables:
    m (gurobipy.Model): Gurobi model instance
    P (list): List of all professors
    PP (list): List of permanent professors
    PS (list): List of substitute professors
    D (dict): Dictionary of courses
    DISCIPLINA_DIAS (list): List of days for each course
    DISCILINA_HORARIOS (list): List of times for each course
    f (dict): Coefficients for the objective function
    X (dict): Decision variables for the model
    PNC (dict): Slack variables indicating how many credits a professor is below the ideal

Functions:
    get_disciplinas_dias_horarios(D): Returns the days and times for each course
    professor_apto(p): Returns the courses a professor is qualified to teach
    utils.get_carga_horaria(D, d): Returns the workload for a given course
    get_disciplinas_a_partir_de_um_dia(D, day): Returns the courses on a given day
    get_disciplinas_a_partir_de_um_horario(D, time): Returns the courses at a given time
    get_codigo_disciplinas(D): Returns the codes of all courses

Constraints:
    RF1: Ensures permanent professors are allocated the suggested number of credits if possible
    RH2: Limits the maximum number of credits for substitute professors
    RH3: Ensures each course is taught by only one professor
    RH4: Ensures a professor teaches at most one course at the same time
    RH5: Ensures a professor does not teach a course they are not qualified for

Objective:
    Maximize the allocation of professors to courses while minimizing the slack variables for permanent professors
Usage:

    Run the script to solve the course timetabling problem and print the results.
"""

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
courses = input.disciplinas
course_days, course_times = utils.get_disciplinas_dias_horarios(courses)

# Coefficients and variables
coefficients = {}
variables = {}

def initialize_variables_and_coefficients():
    for professor in professors:
        coefficients[professor] = {}
        variables[professor] = {}
        qualified_courses = utils.professor_apto(professor)

        for course in courses.keys():
            coefficients[professor][course] = {}
            variables[professor][course] = {}

            workload = utils.get_carga_horaria(courses, course)
            day, time = workload

            coefficients[professor][course][day] = {}
            coefficients[professor][course][day][time] = (
                DUMMY_COEFFICIENT if professor == DUMMY_PROFESSOR else
                DEFAULT_COEFFICIENT if course in qualified_courses else
                ZERO_COEFFICIENT
            )

            variables[professor][course][day] = {}
            variables[professor][course][day][time] = model.addVar(
                vtype=GRB.BINARY, name=f"{professor}_{course}_{day}_{time}"
            )

def add_slack_variables():
    slack_variables = {}
    for professor in permanent_professors:
        slack_variables[professor] = model.addVar(vtype=GRB.INTEGER, name=f"PNC_{professor}")
    return slack_variables

def add_constraints(slack_variables):
    # Soft constraints
    for professor in permanent_professors:
        model.addConstr(
            gp.quicksum(
                variables[professor][course][utils.get_carga_horaria(courses, course)[0]][utils.get_carga_horaria(courses, course)[1]] * courses[course][2]
                for course in courses.keys()
            ) == MIN_CREDITS_PERMANENT - slack_variables[professor]
        )

    # Hard constraints
    for professor in substitute_professors:
        model.addConstr(
            gp.quicksum(
                variables[professor][course][utils.get_carga_horaria(courses, course)[0]][utils.get_carga_horaria(courses, course)[1]] * courses[course][2]
                for course in courses.keys()
            ) <= MAX_CREDITS_SUBSTITUTE
        )

    for course in courses.keys():
        workload = utils.get_carga_horaria(courses, course)
        day, time = workload
        model.addConstr(gp.quicksum(variables[professor][course][day][time] for professor in professors) == 1)

    for professor in professors:
        if professor == DUMMY_PROFESSOR:
            continue
        for i in range(len(course_days)):
            day = course_days[i]
            time = course_times[i]
            day_courses = utils.get_disciplinas_a_partir_de_um_dia(courses, day)
            time_courses = utils.get_disciplinas_a_partir_de_um_horario(courses, time)
            common_courses = day_courses.intersection(time_courses)
            model.addConstr(
                gp.quicksum(
                    variables[professor][course][utils.get_carga_horaria(courses, course)[0]][utils.get_carga_horaria(courses, course)[1]]
                    for course in common_courses
                ) <= 1
            )

    for professor in professors:
        all_courses = utils.get_codigo_disciplinas(courses)
        qualified_courses = utils.professor_apto(professor)
        unqualified_courses = all_courses.difference(qualified_courses)
        model.addConstr(
            gp.quicksum(
                variables[professor][course][utils.get_carga_horaria(courses, course)[0]][utils.get_carga_horaria(courses, course)[1]]
                for course in unqualified_courses
            ) == 0
        )

def set_objective(slack_variables):
    model.setObjective(
        gp.quicksum(
            variables[professor][course][day][time] * coefficients[professor][course][day][time]
            for professor in professors
            for course in courses.keys()
            for day, time in [utils.get_carga_horaria(courses, course)]
        ) - gp.quicksum(WEIGHT_FACTOR * slack_variables[professor] for professor in permanent_professors),
        GRB.MAXIMIZE
    )

def main():
    initialize_variables_and_coefficients()
    slack_variables = add_slack_variables()
    add_constraints(slack_variables)
    set_objective(slack_variables)
    model.update()
    model.optimize()

    print("========= RESULT ==========")
    for var in model.getVars():
        if var.X > 0:
            print(f"{var.VarName} {var.X}")
    print("=============================")
    print(f"Obj: {model.ObjVal}")

if __name__ == "__main__":
    main()
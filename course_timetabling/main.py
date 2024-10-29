import gurobipy as gp
from gurobipy import GRB

from utils import utils
from database.construct_sets import (
    get_courses_set,
    get_elective_courses_set, #TODO implementar matérias eletivas com um coeficiente mais baixo
    get_manual_allocation_set,
    get_professors_set,
)


# Constants
DUMMY_PROFESSOR = "DUMMY"
DUMMY_COEFFICIENT = 0.0001
DEFAULT_COEFFICIENT = 100
SERVICE_COURSE_COEFFICIENT = 10 # TODO: implementar um coeficiente para disciplinas de serviço
ELECTIVE_COEFFICIENT = 1
ZERO_COEFFICIENT = 0
WEIGHT_FACTOR = 1000
MIN_CREDITS_PERMANENT = 8
MAX_CREDITS_SUBSTITUTE = 12


class CourseTimetabling:
    def __init__(
        self,
        professors,
        permanent_professors,
        substitute_professors,
        courses,
        manual_allocation,
    ):
        self.professors = professors
        self.permanent_professors = permanent_professors
        self.substitute_professors = substitute_professors
        self.courses = courses
        self.manual_allocation = manual_allocation
        self.model = gp.Model("CourseTimetabling")
        self.coefficients = {}
        self.variables = {}
        self.slack_variables = {}

    def set_courses(self, courses):
        self.courses = courses

    def initialize_variables_and_coefficients(self):
        """
        Initializes the variables and coefficients for the course timetabling problem.
        This method sets up the coefficients and variables for each professor and course
        based on their qualifications and manual allocations. It iterates through the list
        of professors and courses, and for each combination, it determines the appropriate
        coefficient and creates a binary variable for the scheduling model.
        The coefficients are determined based on whether the professor is a dummy professor,
        if the course is available for the professor, or if it is manually allocated. The
        variables are added to the model as binary variables representing whether a professor
        is assigned to a course at a specific day and time.
        Constants:
            DUMMY_COEFFICIENT: The coefficient value for dummy professors.
            DEFAULT_COEFFICIENT: The default coefficient value for qualified courses.
            ZERO_COEFFICIENT: The coefficient value for unqualified courses.
            DUMMY_PROFESSOR: A constant representing a dummy professor.
        """
        for professor in self.professors:
            self.coefficients[professor] = {}
            self.variables[professor] = {}
            qualified_courses = utils.get_qualified_courses_for_professor(
                self.courses, self.professors, professor
            )

            qualified_courses_available = utils.add_manual_allocation_courses(
                professor, qualified_courses, self.manual_allocation
            )

            for course in self.courses.keys():
                self.coefficients[professor][course] = {}
                self.variables[professor][course] = {}

                workload = utils.get_course_schedule(self.courses, course)
                day, time = workload

                self.coefficients[professor][course][day] = {}

                if professor == DUMMY_PROFESSOR:
                    self.coefficients[professor][course][day][time] = DUMMY_COEFFICIENT
                else:
                    if course in qualified_courses_available:
                        if self.courses[course]["course_type"] == "OPT":
                            self.coefficients[professor][course][day][time] = ELECTIVE_COEFFICIENT
                        else:
                            self.coefficients[professor][course][day][time] = DEFAULT_COEFFICIENT
                    else:
                        self.coefficients[professor][course][day][time] = ZERO_COEFFICIENT
       
                # self.coefficients[professor][course][day][time] = (
                #     DUMMY_COEFFICIENT
                #     if professor == DUMMY_PROFESSOR
                #     else (
                #         DEFAULT_COEFFICIENT
                #         if course in qualified_courses_available
                #         else ZERO_COEFFICIENT
                #     )
                # )

                self.variables[professor][course][day] = {}
                self.variables[professor][course][day][time] = self.model.addVar(
                    vtype=GRB.BINARY, name=f"{professor}_{course}_{day}_{time}"
                )

    def add_credit_slack_variables(self):
        """
        Adds slack variables for credit allocation to the model.

        This method creates a slack variable for each permanent professor, indicating
        how many credits the permanent professor is below the ideal number set by the coordination.
        The slack variables are added to the model and stored in the `slack_variables`
        dictionary with the professor as the key.

        Attributes:
            permanent_professors (list): A list of permanent professors.
            slack_variables (dict): A dictionary to store the slack variables for each professor.
            model (gurobipy.Model): The optimization model to which the slack variables are added.
        """
        for professor in self.permanent_professors:
            self.slack_variables[professor] = self.model.addVar(
                vtype=GRB.INTEGER, name=f"PNC_{professor}"
            )

    def add_constraints(self):
        course_days, course_times = utils.get_possible_schedules(self.courses)

        # Manual
        # RH1: Alocar manualmente os professores
        for course_class_id in self.manual_allocation.keys():
            professor = self.manual_allocation[course_class_id]["professor"]
            day = self.manual_allocation[course_class_id]["day"]
            time = self.manual_allocation[course_class_id]["time"]

            self.model.addConstr(
                self.variables[professor][course_class_id][day][time] == 1
            )

        # Soft constraints
        # RF1: Garante que o professor seja alocado com a quantidade de créditos sujerida pela coordenação se possível. Não inviabilisa o modelo caso não seja atingido.
        for professor in self.permanent_professors:
            self.model.addConstr(
                gp.quicksum(
                    self.variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    * self.courses[course]["credits"]
                    for course in self.courses.keys()
                )
                == MIN_CREDITS_PERMANENT - self.slack_variables[professor]
            )

        # Hard constraints
        # RH2: Regime de trabalho (quantidade de horas) - quantidade de créditos máximo para o professor substituto
        for professor in self.substitute_professors:
            self.model.addConstr(
                gp.quicksum(
                    self.variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    * self.courses[course]["credits"]
                    for course in self.courses.keys()
                )
                <= MAX_CREDITS_SUBSTITUTE
            )

        # RH3: Uma disciplina de uma turma, deverá ser ministrada por um único professor
        for course in self.courses.keys():
            workload = utils.get_course_schedule(self.courses, course)
            day, time = workload
            self.model.addConstr(
                gp.quicksum(
                    self.variables[professor][course][day][time]
                    for professor in self.professors
                )
                == 1
            )

        # RH4: Um professor poderá dar no máximo 1 disciplina de uma turma em um mesmo dia e horário (binário OU <= 1)
        for professor in self.professors:
            if professor == DUMMY_PROFESSOR:
                continue
            for i in range(len(course_days)):
                day = course_days[i]
                time = course_times[i]
                day_courses = utils.get_courses_by_day(self.courses, day)
                time_courses = utils.get_courses_by_time(self.courses, time)
                common_courses = day_courses.intersection(time_courses)
                self.model.addConstr(
                    gp.quicksum(
                        self.variables[professor][course][
                            utils.get_course_schedule(self.courses, course)[0]
                        ][utils.get_course_schedule(self.courses, course)[1]]
                        for course in common_courses
                    )
                    <= 1
                )

        # RH5: Um professor não pode lecionar uma disciplina em que ele não esteja apto
        # Caso o professor seja alocado manualmente, ele não precisa lecionar uma disciplina que esteja apto (sem verificação)
        for professor in self.professors:
            all_courses = utils.get_all_course_class_id(self.courses)
            courses_available = utils.remove_manual_allocation_courses(
                all_courses, self.manual_allocation
            )

            qualified_courses = utils.get_qualified_courses_for_professor(
                self.courses, self.professors, professor
            )
            unqualified_courses = courses_available.difference(qualified_courses)
            self.model.addConstr(
                gp.quicksum(
                    self.variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    for course in unqualified_courses
                )
                == 0
            )

    def set_objective(self):
        self.model.setObjective(
            gp.quicksum(
                self.variables[professor][course][day][time]
                * self.coefficients[professor][course][day][time]
                for professor in self.professors
                for course in self.courses.keys()
                for day, time in [utils.get_course_schedule(self.courses, course)]
            )
            - gp.quicksum(
                WEIGHT_FACTOR * self.slack_variables[professor]
                for professor in self.permanent_professors
            ),
            GRB.MAXIMIZE,
        )

    def optimize(self):
        self.model.update()
        self.model.optimize()

    def generate_results(self):

        professor_timeschedule = []
        for var in self.model.getVars():
            if var.X > 0:
                timeschedule = f"{var.VarName}/{var.X}"
                professor_timeschedule.append(timeschedule)

        model_value = self.model.ObjVal
        print("========= RESULT ==========")
        for r in professor_timeschedule:
            print(r)
        print("=============================")
        print(f"Obj: {model_value}")
        return professor_timeschedule, model_value


def main():
    MANUAL_ALLOCATION = get_manual_allocation_set()

    professors_permanent_set, professors_substitute_set, professor_dummy = (
        get_professors_set()
    )
    professors_set = (
        professors_permanent_set | professors_substitute_set | professor_dummy
    )
    PROFESSORS = professors_set
    PERMANENT_PROFESSORS = professors_permanent_set
    SUBSTITUTE_PROFESSORS = professors_substitute_set

    required_courses = get_courses_set(MANUAL_ALLOCATION)
    elective_courses = get_elective_courses_set()
    COURSES = utils.get_all_available_courses_for_allocation(required_courses, elective_courses, PROFESSORS)

    timetabling = CourseTimetabling(
        PROFESSORS,
        PERMANENT_PROFESSORS,
        SUBSTITUTE_PROFESSORS,
        COURSES,
        MANUAL_ALLOCATION,
    )
    timetabling.initialize_variables_and_coefficients()
    timetabling.add_credit_slack_variables()
    timetabling.add_constraints()
    timetabling.set_objective()
    timetabling.optimize()
    timetabling.generate_results()


if __name__ == "__main__":
    main()

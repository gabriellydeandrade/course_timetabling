import gurobipy as gp
from gurobipy import GRB

import settings

from utils import utils
from database.construct_sets import (
    get_courses_set,
    get_manual_allocation_set,
    get_professors_set,
)


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
        self.EAP_coefficient = {}
        self.X_variables = {}
        self.PP_slack_variables = {}
        self.PS_slack_variables = {}

        self.env = self.init_environment()
        self.model = gp.Model(name="CourseTimetabling", env=self.env)

    def init_environment(self):
        if settings.APP_LICENSE_TYPE == settings.LicenseType.NAMED_USER_ACADEMIC.value:
            env = gp.Env(empty=False)

        elif settings.APP_LICENSE_TYPE == settings.LicenseType.WSL_ACADEMIC.value:
            env = gp.Env(empty=True)
            env.setParam("LicenseID", settings.APP_LICENSE_ID)
            env.setParam("WLSAccessID", settings.APP_WLS_ACCESS_ID)
            env.setParam("WLSSecret", settings.APP_WS_SECRET)

        env.start()

        return env

    def set_courses(self, courses):
        self.courses = courses

    def initialize_variables_and_coefficients(self):
        """
        Initializes the binary variables and coefficients for the course timetabling problem.

        Constants:
            settings.DUMMY_PROFESSOR_NAME: A constant representing a dummy professor.
            settings.DUMMY_COEFFICIENT: The coefficient value for dummy professors.
            settings.DEFAULT_COEFFICIENT: The default coefficient value for qualified courses.
            settings.ZERO_COEFFICIENT: The coefficient value for unqualified courses.
        """
        for professor in self.professors:
            self.EAP_coefficient[professor] = {}
            self.X_variables[professor] = {}

            qualified_courses = utils.get_qualified_courses_for_professor(
                self.courses, self.professors, professor
            )
            qualified_courses_with_manual_allocation = (
                utils.add_manual_allocation_courses(
                    professor, qualified_courses, self.manual_allocation
                )
            )

            for course in self.courses.keys():
                self.EAP_coefficient[professor][course] = {}
                self.X_variables[professor][course] = {}

                workload = utils.get_course_schedule(self.courses, course)
                day, time = workload

                self.EAP_coefficient[professor][course][day] = {}

                EAPI = 0
                EAPP = 0
                EAPS = 0

                if professor == settings.DUMMY_PROFESSOR_NAME:
                    EAPI = settings.DUMMY_COEFFICIENT
                else:
                    if self.courses[course]["course_type"] == "SVC" and any(
                        cid in settings.SVC_BASIC_COURSES
                        for cid in self.courses[course]["course_id"].split(",")
                    ):
                        if self.professors[professor]["category"] == "PS":
                            EAPI = settings.SERVICE_COURSE_COEFFICIENT_SP
                        else:
                            EAPI = settings.SERVICE_COURSE_COEFFICIENT_PP
                    elif course in qualified_courses_with_manual_allocation:
                        EAPI = settings.DEFAULT_COEFFICIENT
                    else:
                        EAPI = settings.ZERO_COEFFICIENT

                if EAPI:
                    self.EAP_coefficient[professor][course][day][time] = (
                        EAPI + EAPP + EAPS
                    )
                else:
                    self.EAP_coefficient[professor][course][day][time] = 0

                self.X_variables[professor][course][day] = {}
                self.X_variables[professor][course][day][time] = self.model.addVar(
                    vtype=GRB.BINARY, name=f"{professor}_{course}_{day}_{time}"
                )

    def add_credit_slack_variables(self):
        """
        Adds slack variables for credit allocation to the model.

        This method creates a slack variable for each permanent professor, indicating
        how many credits the permanent professor is below the ideal number set by the coordination.

        Attributes:
            permanent_professors (list): A list of permanent professors.
            slack_variables (dict): A dictionary to store the slack variables for each professor.
            model (gurobipy.Model): The optimization model to which the slack variables are added.
        """
        for professor in self.permanent_professors:
            self.PP_slack_variables[professor] = self.model.addVar(
                vtype=GRB.INTEGER, name=f"PCB_{professor}"
            )

        for professor in self.substitute_professors:
            self.PS_slack_variables[professor] = self.model.addVar(
                vtype=GRB.INTEGER, name=f"PSB_{professor}"
            )

    def add_constraints(self):
        course_days, course_times = utils.get_possible_schedules(self.courses)

        # Manual
        # RNP1: Alocar manualmente os professores
        for course_class_id in self.manual_allocation.keys():
            professor = self.manual_allocation[course_class_id]["professor"]
            day = self.manual_allocation[course_class_id]["day"]
            time = self.manual_allocation[course_class_id]["time"]

            self.model.addConstr(
                self.X_variables[professor][course_class_id][day][time] == 1
            )

        # Soft constraints
        # RNG1: Garante que o professor permanente seja alocado com a quantidade de créditos sujerida pela coordenação se possível. Não inviabiliza o modelo caso não seja atingido.
        for professor in self.permanent_professors:
            self.model.addConstr(
                gp.quicksum(
                    self.X_variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    * self.courses[course]["credits"]
                    for course in self.courses.keys()
                )
                == settings.MIN_CREDITS_PERMANENT - self.PP_slack_variables[professor]
            )

        for professor in self.substitute_professors:
            # RNG2: Garante que o professor permanente seja alocado com a quantidade de créditos sujerida pela coordenação se possível. Não inviabiliza o modelo caso não seja atingido.
            self.model.addConstr(
                gp.quicksum(
                    self.X_variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    * self.courses[course]["credits"]
                    for course in self.courses.keys()
                )
                == settings.MIN_CREDITS_SUBSTITUTE - self.PS_slack_variables[professor]
            )

            # Hard constraints

            # RNP2: Regime de trabalho (quantidade de horas) - quantidade de créditos máximo para o professor efetivo
            self.model.addConstr(
                gp.quicksum(
                    self.X_variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    * self.courses[course]["credits"]
                    for course in self.courses.keys()
                )
                <= settings.MAX_CREDITS_PERMANENT
            )

            # RNP3: Regime de trabalho (quantidade de horas) - quantidade de créditos máximo para o professor substituto
            self.model.addConstr(
                gp.quicksum(
                    self.X_variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    * self.courses[course]["credits"]
                    for course in self.courses.keys()
                )
                <= settings.MAX_CREDITS_SUBSTITUTE
            )

        # RNG3: Uma disciplina de uma turma, deverá ser ministrada por um único professor
        for course in self.courses.keys():
            workload = utils.get_course_schedule(self.courses, course)
            day, time = workload
            self.model.addConstr(
                gp.quicksum(
                    self.X_variables[professor][course][day][time]
                    for professor in self.professors
                )
                == 1
            )

        # RNG4: Um professor poderá dar no máximo 1 disciplina de uma turma em um mesmo dia e horário (binário OU <= 1)
        for professor in self.professors:
            if professor == settings.DUMMY_PROFESSOR_NAME:
                continue
            for i in range(len(course_days)):
                day = course_days[i]
                time = course_times[i]

                day_courses = utils.get_courses_by_day(self.courses, day)
                time_courses = utils.get_courses_by_time(self.courses, time)
                common_courses = day_courses.intersection(time_courses)

                exact_time_courses = utils.get_courses_by_exact_day_and_time(
                    self.courses, day, time
                )
                conflict_courses = common_courses.difference(exact_time_courses)

                self.model.addConstr(
                    gp.quicksum(
                        self.X_variables[professor][course][day][time]
                        for course in exact_time_courses
                    )
                    <= 1
                )

                # Adiciona restrição para garantir que se uma variável for 1, as outras sejam 0
                for course in exact_time_courses:
                    for cc in conflict_courses:
                        self.model.addConstr(
                            self.X_variables[professor][course][day][time]
                            + self.X_variables[professor][cc][
                                utils.get_course_schedule(self.courses, cc)[0]
                            ][utils.get_course_schedule(self.courses, cc)[1]]
                            <= 1
                        )

        # RNG5: Um professor não pode lecionar uma disciplina em que ele não esteja apto
        # Caso o professor seja alocado manualmente, ele não precisa lecionar uma disciplina que esteja apto (sem verificação)
        for professor in self.professors:
            all_courses = utils.get_all_course_class_id(self.courses)
            courses_available = utils.remove_courses(
                all_courses, self.manual_allocation
            )

            qualified_courses = utils.get_qualified_courses_for_professor(
                self.courses, self.professors, professor
            )
            unqualified_courses = courses_available.difference(qualified_courses)
            self.model.addConstr(
                gp.quicksum(
                    self.X_variables[professor][course][
                        utils.get_course_schedule(self.courses, course)[0]
                    ][utils.get_course_schedule(self.courses, course)[1]]
                    for course in unqualified_courses
                )
                == 0
            )

    def set_objective(self):
        self.model.setObjective(
            gp.quicksum(
                self.X_variables[professor][course][
                    utils.get_course_schedule(self.courses, course)[0]
                ][utils.get_course_schedule(self.courses, course)[1]]
                * self.EAP_coefficient[professor][course][
                    utils.get_course_schedule(self.courses, course)[0]
                ][utils.get_course_schedule(self.courses, course)[1]]
                for professor in self.professors
                for course in self.courses.keys()
            )
            - gp.quicksum(
                settings.WEIGHT_FACTOR_PP * self.PP_slack_variables[professor]
                for professor in self.permanent_professors
            )
            - gp.quicksum(
                settings.WEIGHT_FACTOR_PS * self.PS_slack_variables[professor]
                for professor in self.substitute_professors
            ),
            GRB.MAXIMIZE,
        )

    def optimize(self):
        self.model.update()
        self.model.optimize()

    def clean_model(self):
        self.model.dispose()
        self.env.dispose()

    def generate_results(self):

        if self.model.Status == 2:
            print(f"Optimal solution found. Model return status={self.model.Status}")
        else:
            self.model.computeIIS()
            self.model.write("model.ilp")
            raise Exception(f"Model return status={self.model.Status}")

        timeschedule = []
        for var in self.model.getVars():
            if var.X > 0:
                allocation = f"{var.VarName}/{var.X}"
                timeschedule.append(allocation)

        model_value = self.model.ObjVal

        utils.treat_and_save_results(timeschedule, self.courses)

        print("========= METHOD ==========")
        print(self.model.getParamInfo("Method"))
        print(self.model.getParamInfo("ConcurrentMethod"))
        print(self.model.getParamInfo("ConcurrentMIP"))

        print(f"É MIP: {self.model.getAttr(GRB.Attr.IsMIP)}")
        print(f"É QP: {self.model.getAttr(GRB.Attr.IsQP)}")
        print(f"É QCP: {self.model.getAttr(GRB.Attr.IsQCP)}")
        print(f"É MultiObj: {self.model.getAttr(GRB.Attr.IsMultiObj)}")
        print("=============================")

        print("========= RESULT ==========")
        print("Result was saved in results/*")
        print("=============================")
        print(f"Obj: {model_value}")

        return timeschedule, model_value


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

    COURSES = get_courses_set(MANUAL_ALLOCATION)

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
    timetabling.clean_model()


if __name__ == "__main__":
    main()

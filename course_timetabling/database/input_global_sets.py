from database.construct_sets import get_courses_set, get_professors_set

courses_set = get_courses_set()

professors_permanent_set, professors_substitute_set = get_professors_set()
professors_set = professors_permanent_set | professors_substitute_set

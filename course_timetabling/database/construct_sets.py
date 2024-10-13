from database.service_google_sheet import get_required_courses
from database.transform_data import transform_required_courses_to_dict

def get_courses_set():
    required_courses = get_required_courses()
    courses_set = transform_required_courses_to_dict(required_courses)

    return courses_set

def get_course_schedule(courses_set, course_id: str):
    return courses_set[course_id]["day"], courses_set[course_id]["time"]

# elective_courses = get_courses("disciplinas_eletivas!A:J")

# permanent, substitute = get_professors()
# permanent_professors = treat_professors_expertise(permanent, elective_courses)
# substitute_professors = treat_professors_expertise(substitute, elective_courses, type="substitute")
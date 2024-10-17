from database.service_google_sheet import (
    get_required_courses,
    get_elective_courses,
    get_professors,
)
from database.transform_data import (
    transform_courses_to_dict,
    transform_professors_to_dict,
)


def get_courses_set() -> dict[str, dict]:
    """
    Retrieves a set of required courses and transforms them into a dictionary format.

    Returns:
        dict: A dictionary containing the transformed required courses.
    """
    required_courses = get_required_courses()
    courses_set = transform_courses_to_dict(required_courses)

    return courses_set


def get_course_schedule(courses_set, course_class_id: str):
    """
    Retrieve the schedule for a specific course class.

    Args:
        courses_set (dict): A dictionary containing course information.
        course_class_id (str): The ID of the course class to retrieve the schedule for.

    Returns:
        tuple: A tuple containing the day and time of the course class.
    """
    return courses_set[course_class_id]["day"], courses_set[course_class_id]["time"]


def get_elective_courses_set():
    """
    Retrieves a set of elective courses and transforms them into a dictionary format.
    Obs.: Do not contain a time schedule due to the nature of elective courses.

    Returns:
        dict: A dictionary containing the elective courses.
    """
    elective_courses = get_elective_courses()
    courses_set = transform_courses_to_dict(elective_courses)

    return courses_set


def get_professors_set() -> tuple[dict, dict]:
    """
    Retrieves a set of professors and transforms them into a dictionary format.

    Returns:
        dict: A dictionary containing the transformed professors.
    """
    permanent, substitute = get_professors()
    professors_permanent_set = transform_professors_to_dict(permanent)
    professors_substitute_set = transform_professors_to_dict(substitute)

    # TODO adiciona expertise dos professores e serviço com a chamada treat_professors_expertise

    return professors_permanent_set, professors_substitute_set

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

    #TODO acrescentar professor dummy novamente

    # TODO adiciona expertise dos professores e serviço com a chamada treat_professors_expertise

    return professors_permanent_set, professors_substitute_set

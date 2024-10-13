from database.service_google_sheet import get_required_courses, get_elective_courses
from database.transform_data import transform_courses_to_dict

def get_courses_set():
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


# permanent, substitute = get_professors()
# permanent_professors = treat_professors_expertise(permanent, elective_courses)
# substitute_professors = treat_professors_expertise(substitute, elective_courses, type="substitute")
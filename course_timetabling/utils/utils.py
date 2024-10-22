from typing import Tuple

def get_qualified_courses_for_professor(courses_set: dict, professors_set: dict, professor: str) -> set:
    """
    Verifies if the professor is qualified to teach the discipline.
    Returns a set with the disciplines they can teach.

    Args:
        professors_set (dict): A dictionary containing professor information.
        professor (str): The name or identifier of the professor.

    Returns:
        set: A set of disciplines the professor is qualified to teach.
    """
    qualified_course_class_id = []

    if professor == "DUMMY":
        # In the case of a DUMMY professor, they can teach any discipline from all areas
        qualified_course_class_id = list(courses_set.keys())
    else:
        try:
            qualified_courses = professors_set[professor]["qualified_courses"]
        except KeyError:
            print(f"====Professor {professor} not found in the list of discipline profiles")
            return set()
        
        for course_class_id in courses_set.keys():
            if courses_set[course_class_id]["course_id"] in qualified_courses:
                qualified_course_class_id.append(course_class_id)
    
    return set(qualified_course_class_id)


def get_possible_schedules(courses: dict) -> Tuple[list,list]:
    """
    Extracts and returns the unique days and times from a dictionary of courses.
    Args:
        courses (dict): A dictionary where the keys are course identifiers and the values are dictionaries 
                        containing course details, specifically 'day' and 'time'.
    Returns:
        tuple: A tuple containing two lists:
            - days (list): A list of unique days on which the courses are scheduled.
            - time (list): A list of unique times at which the courses are scheduled.
    """
    days = []
    times = []

    for _, course_details in courses.items():
        day = course_details['day']
        time = course_details['time']

        days.append(day)
        times.append(time)
    
    days = list(set(days))
    times = list(set(times))

    return days, times

def get_course_schedule(courses_set: dict, course_class_id: str) -> Tuple[str, str]:
    """
    Retrieve the schedule for a specific course class.

    Args:
        courses_set (dict): A dictionary containing course information.
        course_class_id (str): The ID of the course class to retrieve the schedule for.

    Returns:
        tuple: A tuple containing the day and time of the course class.
    """
    return courses_set[course_class_id]["day"], courses_set[course_class_id]["time"]

def get_all_course_class_id(courses: dict) -> set:
    result = set([d for d in courses.keys()])
    return result


def get_courses_by_time(courses: dict, time: str) -> set:
    """
    Returns a set of courses that have classes at the specified time.

    Args:
        courses (dict): Dictionary containing course details.
        time (str): The time to filter courses by.

    Returns:
        set: A set of courses that have classes at the specified time.
    """
    return {
        course_id
        for course_id, details in courses.items()
        for course_time in details["time"].split(",")
        if course_time == time
    }

def get_courses_by_day(courses: dict, day: str) -> set:
    """
    Returns a set of courses that have classes on the specified day.

    Args:
        courses (dict): Dictionary containing course details.
        day (str): The day to filter courses by.

    Returns:
        set: A set of courses that have classes on the specified day.
    """
    result = []

    for course_id, details in courses.items():
        for course_day in details["day"].split(","):
            if course_day == day:
                result.append(course_id)

    return set(result)
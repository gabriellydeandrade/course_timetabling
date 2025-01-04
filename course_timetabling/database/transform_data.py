from typing import Dict
import pandas as pd
import numpy as np


def transform_courses_to_dict(courses: pd.DataFrame) -> Dict:
    """
    Transforms a DataFrame of required courses into a dictionary with course details.
    Args:
        courses (pd.DataFrame): A DataFrame containing course information with columns
                                such as 'credits' and indexed by course identifiers.
    Returns:
        dict: A dictionary where each key is a course identifier and each value is a
              dictionary of course details, with the 'credits' field converted to an integer.
    """

    courses = courses.replace({np.nan: None})
    courses_transformed = courses.to_dict("index")

    for course in courses_transformed:
        courses_transformed[course]["credits"] = int(
            courses_transformed[course]["credits"]
        )

    return courses_transformed


def transform_professors_to_dict(professors_availables: pd.DataFrame) -> Dict:
    professors_availables_transformed = professors_availables.to_dict("index")

    for professor in professors_availables_transformed:
        professors_availables_transformed[professor]["qualified_courses"] = (
            professors_availables_transformed[professor]["qualified_courses"].split(",")
            if professors_availables_transformed[professor]["qualified_courses"]
            and type(professors_availables_transformed[professor]["qualified_courses"])
            == str
            else []
        )
        professors_availables_transformed[professor]["expertise"] = (
            professors_availables_transformed[professor]["expertise"].split(",")
            if professors_availables_transformed[professor]["expertise"]
            and type(professors_availables_transformed[professor]["expertise"]) == str
            else []
        )

    return professors_availables_transformed

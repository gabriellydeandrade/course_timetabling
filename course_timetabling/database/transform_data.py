from typing import Dict
from pandera.typing import DataFrame



def transform_courses_to_dict(courses: DataFrame) -> Dict[str, dict]:
    """
    Transforms a DataFrame of required courses into a dictionary with course details.
    Args:
        courses (pd.DataFrame): A DataFrame containing course information with columns 
                                such as 'credits' and indexed by course identifiers.
    Returns:
        dict: A dictionary where each key is a course identifier and each value is a 
              dictionary of course details, with the 'credits' field converted to an integer.
    """
    courses = courses.to_dict("index")
    
    for course in courses:
        courses[course]["credits"] = int(courses[course]["credits"])

    return courses


def transform_professors_to_dict(professors_availables: DataFrame) -> Dict[str, dict]:
    professors_availables = professors_availables.to_dict("index")
    
    for professor in professors_availables:
        professors_availables[professor]["qualified_courses"] = professors_availables[professor]["qualified_courses"].split(",") if professors_availables[professor]["qualified_courses"] else []
        professors_availables[professor]["expertise"] = professors_availables[professor]["expertise"].split(",") if professors_availables[professor]["expertise"] else []

    return professors_availables

def treat_professors_expertise(professors_availables, elective_courses, type="permanent"):

    professors_availables = transform_professors_to_dict(professors_availables)
 
    # TODO implementar chamada para disciplinas de acordo com area do professor. area -> cod_disciplina para as disciplinas eletivas

    if type == "substitute":
        pass #TODO chamar disciplina de serviço para substitutos

    return professors_availables

from service_google_sheet import get_courses, get_professors


def treat_professors_expertise(professors_availables, elective_courses, type="permanent"):
    professors_availables = professors_availables.to_dict("index")
    
    for professor in professors_availables:
        professors_availables[professor]["qualified_courses"] = professors_availables[professor]["qualified_courses"].split(",")
        professors_availables[professor]["expertise"] = professors_availables[professor]["expertise"].split(",")

    # TODO implementar chamada para disciplinas de acordo com area do professor. area -> cod_disciplina para as disciplinas eletivas

    if type == "substitute":
        pass #TODO chamar disciplina de serviço para substitutos

    return professors_availables


# required_courses = get_courses("disciplinas_obrigatorias!A:O")
# elective_courses = get_courses("disciplinas_eletivas!A:J")

permanent, substitute = get_professors()
# permanent_professors = treat_professors_expertise(permanent, elective_courses)
# substitute_professors = treat_professors_expertise(substitute, elective_courses, type="substitute")
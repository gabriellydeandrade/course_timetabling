from service_google_sheet import get_required_courses, get_professors


required_courses = get_required_courses()
# elective_courses = get_courses("disciplinas_eletivas!A:J")

# permanent, substitute = get_professors()
# permanent_professors = treat_professors_expertise(permanent, elective_courses)
# substitute_professors = treat_professors_expertise(substitute, elective_courses, type="substitute")
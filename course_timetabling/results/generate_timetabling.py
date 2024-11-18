import streamlit as st
import pandas as pd

df = pd.read_csv(
    "course_timetabling/results/timeschedule.csv",
    delimiter=";",
    names=[
        "responsable_institute",
        "professor",
        "course_id",
        "course_name",
        "day",
        "time",
        "capacity",
        "classroom_type",
        "course_type",
        "term"
    ],
)

st.set_page_config(
    layout="wide",
)

st.title("Course Timetabling - Resultados")
st.header("Alocação final de professores em disciplinas", divider="gray")

with st.container(border=True) as general:

    general_without_dummy = df.loc[df["professor"] != "DUMMY"]

    courses_svc = df.loc[df["course_type"] == "SVC"]
    courses_opt = df.loc[df["course_type"] == "OPT"]
    courses_obg = df.loc[df["course_type"] == "OBG"]

    st.subheader("Visão geral")

    st.metric(label="Qtd de disciplinas obrigatórias", value=len(courses_obg))
    st.metric(label="Qtd de disciplinas de serviço", value=len(courses_svc))
    st.metric(label="Qtd de disciplinas eletivas", value=len(courses_opt))

    st.data_editor(
        general_without_dummy,
        column_config={
            "responsable_institute": "Instituto responsável",
            "professor": "Docente",
            "course_id": "Código disciplina",
            "course_name": "Nome disciplina",
            "day": st.column_config.ListColumn(
                "Dia da Semana",
                help="Dia da semana que a disciplina é ministrada",
                width="medium",
            ),
            "time": st.column_config.ListColumn(
                "Horário",
                help="Horário que a disciplina é ministrada",
                width="medium",
            ),
            "capacity": "Vagas",
            "classroom_type": "Tipo de sala",
        },
        hide_index=True,
        use_container_width=False,
    )

with st.container(border=True) as dummy:
    dummy = df.loc[df["professor"] == "DUMMY"]

    st.subheader("Visão professores DUMMY")
    st.text("Disciplinas que não possuem professores, mas que deveriam por serem disciplinas obrigatórias.")

    st.metric(label="Qtd de DUMMY", value=len(dummy), help=f"Existem {len(dummy)} disciplinas sem professores.")

    st.data_editor(
        dummy,
        column_config={
            "responsable_institute": "Instituto responsável",
            "professor": "Docente",
            "course_id": "Código disciplina",
            "course_name": "Nome disciplina",
            "day": st.column_config.ListColumn(
                "Dia da Semana",
                help="Dia da semana que a disciplina é ministrada",
                width="medium",
            ),
            "time": st.column_config.ListColumn(
                "Horário",
                help="Horário que a disciplina é ministrada",
                width="medium",
            ),
            "capacity": "Vagas",
            "classroom_type": "Tipo de sala",
        },
        hide_index=True,
        use_container_width=False,
    )
    

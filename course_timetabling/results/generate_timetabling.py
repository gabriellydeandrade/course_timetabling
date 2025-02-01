import streamlit as st
import pandas as pd

df = pd.read_csv(
    "course_timetabling/results/timeschedule.csv",
    delimiter=";",
    names=[
        "responsable_institute",
        "graduation_course",
        "professor",
        "course_id",
        "course_name",
        "day",
        "time",
        "capacity",
        "classroom_type",
        "course_type",
        "term",
        "class_type"
    ],
)

df_pcb = pd.read_csv(
    "course_timetabling/results/pcb_professors.csv",
    delimiter=";",
    names=["professor", "credits_below"],
)

df_psb = pd.read_csv(
    "course_timetabling/results/psb_professors.csv",
    delimiter=";",
    names=["professor", "min_classes"],
)

st.set_page_config(
    layout="wide",
)

st.title("Course Timetabling - Resultados")
st.header("Alocação final de professores em disciplinas", divider="rainbow")

with st.container(border=True) as general:

    st.subheader("Visão geral")

    general_without_dummy = df.loc[df["professor"] != "DUMMY"]

    all_professors = general_without_dummy["professor"].unique().tolist()
    all_professors.insert(0, "Todos")

    options = st.multiselect("Seleciona um docente", all_professors, ["Todos"])

    if "Todos" in options:
        selected_professors = general_without_dummy["professor"].unique()
    else:
        selected_professors = options

    df_filter = general_without_dummy[
        general_without_dummy["professor"].isin(selected_professors)
    ]

    courses_svc = df_filter.loc[df_filter["course_type"] == "SVC"]
    courses_opt = df_filter.loc[df_filter["course_type"] == "OPT"]
    courses_obg = df_filter.loc[df_filter["course_type"] == "OBG"]

    col1, col2, col3 = st.columns(3)

    col1.metric(label="Qtd de disciplinas obrigatórias", value=len(courses_obg))
    col2.metric(label="Qtd de disciplinas de serviço", value=len(courses_svc))
    col3.metric(label="Qtd de disciplinas eletivas", value=len(courses_opt))

    st.dataframe(
        df_filter,
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
            "term": "Período",
            "class_type": "Tipo de turma",
            "course_type": "Tipo de disciplina",
            "graduation_course": "Curso de oferta"
        },
        hide_index=True,
        use_container_width=False,
    )

with st.container(border=True) as pcb:
    st.subheader("Professores abaixo da carga horária mínima")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Professores efetivos")
        st.text("Professores que estão abaixo da carga horária mínima de 8 créditos. Oportunidade para serem alocados em outras disciplinas, como eletivas.")

        st.metric(
            label="Qtd de professores",
            value=len(df_pcb),
            help=f"Existem {len(df_pcb)} professores no PCB.",
        )

        df_pcb["credits_below_percent"] = ((df_pcb["credits_below"]) / 8) * 100
        df_pcb = df_pcb.sort_values(by="credits_below_percent", ascending=False)

        st.dataframe(
            df_pcb,
            column_config={
                "professor": "Docente",
                "credits_below": "Qtd de créditos",
                "credits_below_percent": st.column_config.ProgressColumn(
                    label="Percentual abaixo do ideal",
                    min_value=0,
                    max_value=100,
                    format="%f%%",
                ),
            },
            hide_index=True,
            use_container_width=False,
        )

    with col2:
        st.subheader("Professores substitutos")
        st.text("Professores que estão abaixo da carga horária mínima de 8 créditos.")

        st.metric(
            label="Qtd de professores",
            value=len(df_psb),
            help=f"Existem {len(df_psb)} professores substitutos no que não estão alocados.",
        )

        st.dataframe(
            df_psb,
            column_config={
                "professor": "Professor substituto",
                "min_classes": "Qtd de aulas esperada"
            },
            hide_index=True,
            use_container_width=False,
        )

with st.container(border=True) as dummy:
    dummy = df.loc[df["professor"] == "DUMMY"]

    st.subheader("Visão professores DUMMY")
    st.text(
        "Disciplinas que não possuem professores, mas que deveriam por serem disciplinas obrigatórias."
    )

    st.metric(
        label="Qtd de DUMMY",
        value=len(dummy),
        help=f"Existem {len(dummy)} disciplinas sem professores.",
    )

    st.dataframe(
        dummy,
        column_config={
            "responsable_institute": "Instituto responsável",
            "graduation_course": "Curso de oferta",
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
            "course_type": "Tipo de disciplina",
            "term": "Período",
        },
        hide_index=True,
        use_container_width=False,
    )

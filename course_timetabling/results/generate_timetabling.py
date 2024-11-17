import streamlit as st
import pandas as pd

df = pd.read_csv("course_timetabling/results/timeschedule.csv", delimiter=";", names=["responsable_institute", "professor", "course_id", "course_name", "day", "time", "capacity", "classroom_type"])

# data_df = pd.DataFrame(
#     {
#         "professor": ["Adriana Vivacqua", "Daniel Sadoc", "Dummy"],
#         "tipo_disciplina": ["Obrigatória", "Obrigatória", "Eletiva"],
#         "departamento": ["BCC", "BCC", "BCC"],
#         "dia_semana": [
#             ["Segunda", "Quarta"],
#             ["Terça", "Quinta"],
#             ["Indisponível"],
#         ],
#         "horario": [
#             ["13:00 a 15:00", "08:00 a 10:00"],
#             ["15:00 a 17:00"],
#             ["Indisponível"],
#         ],
#     }
# )

with st.container():
    st.data_editor(
        df,
        # column_config={
        #     "professor": "Professor",
        #     "tipo_disciplina": "Tipo de Disciplina",
        #     "departamento": "Departamento",
        #     "dia_semana": st.column_config.ListColumn(
        #         "Dia da Semana",
        #         help="Dia da semana que a disciplina é ministrada",
        #         width="medium",
        #     ),
        #     "horario": st.column_config.ListColumn(
        #         "Horário",
        #         help="Horário que a disciplina é ministrada",
        #         width="medium",
        #     ),
        # },
        hide_index=True,
        use_container_width=False,
    )
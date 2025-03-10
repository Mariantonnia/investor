import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Asegúrate de reemplazar "tu_api_key" con tu clave de API de OpenAI
llm = OpenAI(openai_api_key="tu_api_key")

noticias = [
    "La inflación supera las expectativas, generando preocupación en los mercados.",
    "Empresa tecnológica lanza un nuevo producto innovador, impulsando sus acciones.",
    "Cambios regulatorios en el sector energético generan incertidumbre entre los inversores.",
    "Informe revela un aumento en la inversión en energías renovables, con impacto positivo en el sector.",
    "Tensiones geopolíticas aumentan la volatilidad en los mercados globales."
]

plantilla_reaccion = """
Reacción del inversor: {reaccion}
Analiza el sentimiento y la preocupación expresada:
"""
prompt_reaccion = PromptTemplate(template=plantilla_reaccion, input_variables=["reaccion"])
cadena_reaccion = LLMChain(llm=llm, prompt=prompt_reaccion)

plantilla_perfil = """
Análisis de reacciones: {analisis}
Genera un perfil de inversor con enfoque en E,S,G y aversión al riesgo, dando una puntuación de 0 a 100 para cada pilar (E,S,G) y para el riesgo, en total 4 puntuaciones, significando 0 que no tiene preocupaciones por E,S,G o el riesgo y 100 que está totalmente concienciado y es muy averso al riesgo:
"""
prompt_perfil = PromptTemplate(template=plantilla_perfil, input_variables=["analisis"])
cadena_perfil = LLMChain(llm=llm, prompt=prompt_perfil)

if "contador" not in st.session_state:
    st.session_state.contador = 0
    st.session_state.reacciones = []
    st.session_state.titulares = []

st.title("Análisis de Sentimiento de Inversores")

if st.session_state.contador < len(noticias):
    noticia = noticias[st.session_state.contador]
    st.session_state.titulares.append(noticia)  # Usamos la noticia como titular
    st.write(f"**Titular:** {noticia}")

    # Clave única para cada noticia
    reaccion = st.text_input(f"¿Cuál es tu reacción a esta noticia?", key=f"reaccion_{st.session_state.contador}")

    if reaccion:
        st.session_state.reacciones.append(reaccion)
        st.session_state.contador += 1
        st.rerun()
else:
    analisis_total = ""
    for titular, reaccion in zip(st.session_state.titulares, st.session_state.reacciones):
        st.write(f"**Titular:** {titular}")
        st.write(f"**Reacción:** {reaccion}")
        analisis_reaccion = cadena_reaccion.run(reaccion=reaccion)
        analisis_total += analisis_reaccion + "\n"

    perfil = cadena_perfil.run(analisis=analisis_total)
    st.write(f"**Perfil del inversor:** {perfil}")

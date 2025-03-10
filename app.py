import streamlit as st
from langchain import LLMChain
from langchain_groq import ChatGroq
import os
#from transformers import pipeline
#from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

os.environ["GROQ_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"
# Configurar el modelo de Groq
llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)
noticias = [
    "La inflación supera las expectativas, generando preocupación en los mercados.",
    "Empresa tecnológica lanza un nuevo producto innovador, impulsando sus acciones.",
    "Cambios regulatorios en el sector energético generan incertidumbre entre los inversores.",
    "Informe revela un aumento en la inversión en energías renovables, con impacto positivo en el sector.",
    "Tensiones geopolíticas aumentan la volatilidad en los mercados globales."
]

plantilla_titular = """
Noticia: {noticia}
Genera un titular conciso y atractivo para inversores:
"""
prompt_titular = PromptTemplate(template=plantilla_titular, input_variables=["noticia"])
cadena_titular = LLMChain(llm=llm, prompt=prompt_titular)

plantilla_reaccion = """
Reacción del inversor: {reaccion}
Analiza el sentimiento y la preocupación expresada:
"""
prompt_reaccion = PromptTemplate(template=plantilla_reaccion, input_variables=["reaccion"])
cadena_reaccion = LLMChain(llm=llm, prompt=prompt_reaccion)

plantilla_perfil = """
Análisis de reacciones: {analisis}
Genera un perfil de inversor con enfoque en ESG y aversión al riesgo:
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
    titular = cadena_titular.run(noticia=noticia)
    st.session_state.titulares.append(titular)
    st.write(f"**Titular:** {titular}")

    reaccion = st.text_input(f"¿Cuál es tu reacción a esta noticia?")

    if reaccion:
        st.session_state.reacciones.append(reaccion)
        st.session_state.contador += 1
        st.experimental_rerun()  # Recarga la app para mostrar la siguiente pregunta
else:
    analisis_total = ""
    for titular, reaccion in zip(st.session_state.titulares, st.session_state.reacciones):
        st.write(f"**Titular:** {titular}")
        st.write(f"**Reacción:** {reaccion}")
        analisis_reaccion = cadena_reaccion.run(reaccion=reaccion)
        analisis_total += analisis_reaccion + "\n"

    perfil = cadena_perfil.run(analisis=analisis_total)
    st.write(f"**Perfil del inversor:** {perfil}")

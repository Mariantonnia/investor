import streamlit as st
from langchain import LLMChain
from langchain_groq import ChatGroq
import os
#from transformers import pipeline
#from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
import re
import matplotlib.pyplot as plt

os.environ["GROQ_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"
sheet = client.open_by_key("1X5ZPr7CY0V5EDAffdgslDdYL9caj8ltduOcmCqfGBy8").sheet1  # Reemplázalo con el ID real
# Configurar el modelo de Groq
llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)
noticias = [
    "Repsol, entre las 50 empresas que más responsabilidad histórica tienen en el calentamiento global",
    "Amancio Ortega crea un fondo de 100 millones de euros para los afectados de la dana",
    "Freshly Cosmetics despide a 52 empleados en Reus, el 18% de la plantilla",
    "Wall Street y los mercados globales caen ante la incertidumbre por la guerra comercial y el temor a una recesión",
    "El mercado de criptomonedas se desploma: Bitcoin cae a 80.000 dólares, las altcoins se hunden en medio de una frenética liquidación"
]
plantilla_reaccion = """
Reacción del inversor: {reaccion}
Analiza el sentimiento y la preocupación expresada:
"""
prompt_reaccion = PromptTemplate(template=plantilla_reaccion, input_variables=["reaccion"])
cadena_reaccion = LLMChain(llm=llm, prompt=prompt_reaccion)

plantilla_perfil = """
Análisis de reacciones: {analisis}
Genera un perfil detallado del inversor basado en sus reacciones, enfocándote en los pilares ESG (Ambiental, Social y Gobernanza) y su aversión al riesgo. 
Asigna una puntuación de 0 a 100 para cada pilar ESG y para el riesgo, donde 0 indica ninguna preocupación y 100 máxima preocupación o aversión.
Devuelve las 4 puntuaciones en formato: Ambiental: [puntuación], Social: [puntuación], Gobernanza: [puntuación], Riesgo: [puntuación]
"""
prompt_perfil = PromptTemplate(template=plantilla_perfil, input_variables=["analisis"])
cadena_perfil = LLMChain(llm=llm, prompt=prompt_perfil)

# 📌 Inicializar estado en Streamlit
if "contador" not in st.session_state:
    st.session_state.contador = 0
    st.session_state.reacciones = []
    st.session_state.titulares = []

st.title("Análisis de Sentimiento de Inversores")

if st.session_state.contador < len(noticias):
    noticia = noticias[st.session_state.contador]
    st.session_state.titulares.append(noticia)
    st.write(f"**Titular:** {noticia}")

    reaccion = st.text_input(f"¿Cuál es tu reacción a esta noticia?", key=f"reaccion_{st.session_state.contador}")

    if reaccion:
        # Guardar reacción en la sesión
        st.session_state.reacciones.append(reaccion)

        # 📌 Analizar la reacción con el LLM
        analisis_reaccion = cadena_reaccion.run(reaccion=reaccion)

        # 📌 Generar perfil ESG y de riesgo
        perfil = cadena_perfil.run(analisis=analisis_reaccion)

        # 📌 Extraer puntuaciones con expresiones regulares
        puntuaciones = {
            "Ambiental": int(re.search(r"Ambiental: (\d+)", perfil).group(1)),
            "Social": int(re.search(r"Social: (\d+)", perfil).group(1)),
            "Gobernanza": int(re.search(r"Gobernanza: (\d+)", perfil).group(1)),
            "Riesgo": int(re.search(r"Riesgo: (\d+)", perfil).group(1)),
        }

        # 📌 Guardar datos en Google Sheets
        fila = [f"Inversor_{st.session_state.contador + 1}", reaccion, puntuaciones["Ambiental"], puntuaciones["Social"], puntuaciones["Gobernanza"], puntuaciones["Riesgo"]]
        sheet.append_row(fila)

        # 📌 Pasar al siguiente titular automáticamente
        st.session_state.contador += 1
        st.rerun()

else:
    # 📌 Mostrar análisis final
    st.write("### **Resumen del perfil del inversor**")

    # 📌 Calcular puntuaciones totales
    analisis_total = ""
    for titular, reaccion in zip(st.session_state.titulares, st.session_state.reacciones):
        st.write(f"**Titular:** {titular}")
        st.write(f"**Reacción:** {reaccion}")
        analisis_reaccion = cadena_reaccion.run(reaccion=reaccion)
        analisis_total += analisis_reaccion + "\n"

    perfil = cadena_perfil.run(analisis=analisis_total)
    st.write(f"**Perfil del inversor:** {perfil}")

    # 📌 Extraer puntuaciones del perfil
    puntuaciones = {
        "Ambiental": int(re.search(r"Ambiental: (\d+)", perfil).group(1)),
        "Social": int(re.search(r"Social: (\d+)", perfil).group(1)),
        "Gobernanza": int(re.search(r"Gobernanza: (\d+)", perfil).group(1)),
        "Riesgo": int(re.search(r"Riesgo: (\d+)", perfil).group(1)),
    }

    # 📌 Crear gráfico de barras
    categorias = list(puntuaciones.keys())
    valores = list(puntuaciones.values())

    fig, ax = plt.subplots()
    ax.bar(categorias, valores)
    ax.set_ylabel("Puntuación (0-100)")
    ax.set_title("Perfil del Inversor")

    # 📌 Mostrar gráfico en Streamlit
    st.pyplot(fig)

    # 📌 Guardar perfil final en Google Sheets
    sheet.append_row(["Perfil Final", "", puntuaciones["Ambiental"], puntuaciones["Social"], puntuaciones["Gobernanza"], puntuaciones["Riesgo"]])

    # 📌 Reiniciar la sesión después de completar todas las noticias
    st.session_state.contador = 0
    st.session_state.reacciones = []
    st.session_state.titulares = []

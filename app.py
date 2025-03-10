import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import matplotlib.pyplot as plt
import re # Importa expresiones regulares

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
Genera un perfil detallado del inversor basado en sus reacciones, enfocándote en los pilares ESG (Ambiental, Social y Gobernanza) y su aversión al riesgo. 
Asigna una puntuación de 0 a 100 para cada pilar ESG y para el riesgo, donde 0 indica ninguna preocupación y 100 máxima preocupación o aversión. 
Devuelve las 4 puntuaciones en formato: Ambiental: [puntuación], Social: [puntuación], Gobernanza: [puntuación], Riesgo: [puntuación]
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
    st.session_state.titulares.append(noticia)
    st.write(f"**Titular:** {noticia}")

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
    print(f"Respuesta del modelo:{perfil}") # Imprime la respuesta

    # Extraer puntuaciones del perfil con expresiones regulares
    puntuaciones = {}
    puntuaciones["Ambiental"] = int(re.search(r"Ambiental: (\d+)", perfil).group(1))
    puntuaciones["Social"] = int(re.search(r"Social: (\d+)", perfil).group(1))
    puntuaciones["Gobernanza"] = int(re.search(r"Gobernanza: (\d+)", perfil).group(1))
    puntuaciones["Riesgo"] = int(re.search(r"Riesgo: (\d+)", perfil).group(1))

    # Crear gráfico de barras
    categorias = list(puntuaciones.keys())
    valores = list(puntuaciones.values())

    fig, ax = plt.subplots()
    ax.bar(categorias, valores)
    ax.set_ylabel("Puntuación (0-100)")
    ax.set_title("Perfil del Inversor")

    # Mostrar gráfico en Streamlit
    st.pyplot(fig)

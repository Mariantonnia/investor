import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain import LLMChain, PromptTemplate
from langchain_groq import ChatGroq
import os
import re
import matplotlib.pyplot as plt
import uuid

def connect_to_google_sheets(creds_file, sheet_id):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet("Hoja 1")
    return sheet

def initialize_llm(api_key):
    os.environ["GROQ_API_KEY"] = api_key
    llm = ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    return llm

def analyze_reactions(llm, reactions):
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

    analisis_total = " ".join(reactions)
    perfil = cadena_perfil.run(analisis=analisis_total)
    return perfil

def extract_scores(perfil):
    puntuaciones = {
        "Ambiental": int(re.search(r"Ambiental: (\d+)", perfil).group(1)),
        "Social": int(re.search(r"Social: (\d+)", perfil).group(1)),
        "Gobernanza": int(re.search(r"Gobernanza: (\d+)", perfil).group(1)),
        "Riesgo": int(re.search(r"Riesgo: (\d+)", perfil).group(1))
    }
    return puntuaciones

def plot_scores(puntuaciones):
    categorias = list(puntuaciones.keys())
    valores = list(puntuaciones.values())

    fig, ax = plt.subplots()
    ax.bar(categorias, valores)
    ax.set_ylabel("Puntuación (0-100)")
    ax.set_title("Perfil del Inversor")
    st.pyplot(fig)

def main():
    st.title("Análisis de Sentimiento de Inversores")

    creds_file = "credentials.json"
    sheet_id = "1X5ZPr7CY0V5EDAffdgslDdYL9caj8ltduOcmCqfGBy8"
    api_key = "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"

    try:
        sheet = connect_to_google_sheets(creds_file, sheet_id)
        st.write("✅ Hoja de Google Sheets cargada correctamente.")
    except Exception as e:
        st.write(f"❌ Error al acceder a la hoja de cálculo: {e}")
        st.stop()

    llm = initialize_llm(api_key)

    noticias = [
        "Repsol, entre las 50 empresas que más responsabilidad histórica tienen en el calentamiento global",
        "Amancio Ortega crea un fondo de 100 millones de euros para los afectados de la dana",
        "Freshly Cosmetics despide a 52 empleados en Reus, el 18% de la plantilla",
        "Wall Street y los mercados globales caen ante la incertidumbre por la guerra comercial y el temor a una recesión",
        "El mercado de criptomonedas se desploma: Bitcoin cae a 80.000 dólares, las altcoins se hunden en medio de una frenética liquidación"
    ]

    if "contador" not in st.session_state:
        st.session_state.contador = 0
        st.session_state.reacciones = []
        st.session_state.titulares = []

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
        perfil = analyze_reactions(llm, st.session_state.reacciones)
        st.write(f"**Perfil del inversor:** {perfil}")
        puntuaciones = extract_scores(perfil)
        plot_scores(puntuaciones)

if __name__ == "__main__":
    main()

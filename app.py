import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain import LLMChain, PromptTemplate
from langchain_groq import ChatGroq
import os
import re
import matplotlib.pyplot as plt
import uuid

# Configurar conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

try:
    client = gspread.authorize(creds)
    st.write("✅ Conexión con Google Sheets establecida correctamente.")
except Exception as e:
    st.write(f"❌ Error al conectar con Google Sheets: {e}")
    st.stop()

# Conectar con la hoja de cálculo
SHEET_ID = "1X5ZPr7CY0V5EDAffdgslDdYL9caj8ltduOcmCqfGBy8"
try:
    sheet = client.open_by_key("1X5ZPr7CY0V5EDAffdgslDdYL9caj8ltduOcmCqfGBy8").worksheet("Hoja 1")
    st.write("✅ Hoja de Google Sheets cargada correctamente.")
except Exception as e:
    st.write(f"❌ Error al acceder a la hoja de cálculo: {e}")
    st.stop()

# Configurar el modelo LLM
os.environ["GROQ_API_KEY"] = "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"
lm = ChatGroq(
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

if "contador" not in st.session_state:
    st.session_state.contador = 0
    st.session_state.reacciones = []
    st.session_state.titulares = []

st.title("Análisis de Sentimiento de Inversores")

if st.session_state.contador < len(noticias):
    noticia = noticias[st.session_state.contador]
    resultado_titular = cadena_titular.run(noticia=noticia).strip()
    # Extracción del titular usando expresiones regulares
    match = re.search(r'"([^"]*)"$', resultado_titular) #Busca la ultima frase entre comillas
    if match:
        titular = match.group(1).strip()
    else:
        lines = resultado_titular.split('\n')
        for line in reversed(lines):
            if "<think>" not in line:
                titular = line.strip()
                break
    st.session_state.titulares.append(titular)
    st.write(f"**Titular:** {titular}")

    reaccion = st.text_input(f"Hola, ¿cuál es tu opinión sobre {titular}?", key=f"reaccion_{st.session_state.contador}")

    if reaccion:
        st.session_state.reacciones.append(reaccion)
        st.session_state.contador += 1
        st.rerun()
else:
    analisis_total = ""
    for titular, reaccion in zip(st.session_state.titulares, st.session_state.reacciones):
        #st.write(f"**Titular:** {titular}")
        #st.write(f"**Reacción:** {reaccion}")
        analisis_reaccion = cadena_reaccion.run(reaccion=reaccion)
        analisis_total += analisis_reaccion + "\n"

    perfil = cadena_perfil.run(analisis=analisis_total)
    st.write(f"**Perfil del inversor:** {perfil}")

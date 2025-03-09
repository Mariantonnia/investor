import streamlit as st
from langchain import LLMChain
from langchain_groq import ChatGroq

# Configurar el modelo de Groq
llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# Crear una cadena de procesamiento de lenguaje con LangChain
chain = LLMChain(llm=llm)

# Configurar la interfaz de Streamlit
st.title("Aplicación Básica de LangChain con Streamlit")
st.write("Esta es una aplicación de demostración que utiliza LangChain con el modelo de Groq y Streamlit.")

# Entrada de texto del usuario
user_input = st.text_input("Escribe algo:")

# Procesar la entrada del usuario con LangChain
if user_input:
    response = chain.run(user_input)
    st.write("Respuesta de LangChain:")
    st.write(response)
else:
    st.write("Por favor, escribe algo en la caja de texto.")

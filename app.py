import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json

# =========================
# CONFIGURACIÓN DE LA PÁGINA
# =========================
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# =========================
# ESTILOS CSS (tema oscuro elegante)
# =========================
st.markdown(
    """
    <style>
    /* Fondo general */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }

    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }

    /* Textos generales */
    .stMarkdown, .stText, .stSubheader, .stHeader, .stTitle {
        color: #FFFFFF !important;
    }

    /* Etiquetas de inputs */
    label, .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #FFFFFF !important;
        font-weight: bold;
    }

    /* Caja de texto y selectores */
    textarea, input, select {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
    }

    /* Botones */
    div.stButton > button {
        background-color: #1E1E1E;
        color: #FFFFFF;
        border: 1px solid #FFFFFF;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #FFFFFF;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    /* Selectbox y dropdown */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #555555 !important;
        border-radius: 6px !important;
    }

    /* Fondo del contenedor Lottie */
    div[data-testid="stLottie"] {
        background-color: #000000 !important;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# ANIMACIÓN LOTTIE
# =========================
with open("mistery.json") as source:
    animation = json.load(source)
    st_lottie(animation, width=350)

# =========================
# TÍTULO Y DESCRIPCIÓN
# =========================
st.title("📝 Analizador de Texto con TextBlob")
st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:
- Análisis de sentimiento y subjetividad  
- Extracción de palabras clave  
- Análisis de frecuencia de palabras  
""")

# =========================
# BARRA LATERAL
# =========================
st.sidebar.title("⚙️ Opciones")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# =========================
# FUNCIONES
# =========================
def contar_palabras(texto):
    stop_words = set(["a", "de", "la", "the", "and", "to", "in", "of", "que", "y"])  # simplificado
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

translator = Translator()

def traducir_texto(texto):
    try:
        traduccion = translator.translate(texto, src="es", dest="en")
        return traduccion.text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_originales = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_traducidas = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    frases_combinadas = []
    for i in range(min(len(frases_originales), len(frases_traducidas))):
        frases_combinadas.append({"original": frases_originales[i], "traducido": frases_traducidas[i]})
    contador_palabras, palabras = contar_palabras(texto_ingles)
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Análisis de Sentimiento y Subjetividad")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.write("**Sentimiento:**")
        st.progress(sentimiento_norm)
        if resultados["sentimiento"] > 0.05:
            st.success(f"📈 Positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"📉 Negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"📊 Neutral ({resultados['sentimiento']:.2f})")

        st.write("**Subjetividad:**")
        st.progress(resultados["subjetividad"])
        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")

    with col2:
        st.subheader("🔠 Palabras más frecuentes")
        if resultados["contador_palabras"]:
            palabras_top = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(palabras_top)

    st.subheader("📜 Texto traducido")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original (Español):**")
            st.text(resultados["texto_original"])
        with col2:
            st.markdown("**Traducido (Inglés):**")
            st.text(resultados["texto_traducido"])

    st.subheader("✂️ Frases detectadas")
    if resultados["frases"]:
        for i, frase in enumerate(resultados["frases"][:10], 1):
            try:
                blob_frase = TextBlob(frase["traducido"])
                sent = blob_frase.sentiment.polarity
                emoji = "😊" if sent > 0.05 else "😟" if sent < -0.05 else "😐"
                st.write(f"{i}. {emoji} **Original:** *\"{frase['original']}\"*")
                st.write(f"   **Traducción:** *\"{frase['traducido']}\"* (Sentimiento: {sent:.2f})")
                st.write("---")
            except:
                st.write(f"{i}. **Original:** {frase['original']}")
                st.write(f"   **Traducción:** {frase['traducido']}")
                st.write("---")
    else:
        st.write("No se detectaron frases.")

# =========================
# LÓGICA PRINCIPAL
# =========================
if modo == "Texto directo":
    st.subheader("✍️ Ingresa tu texto para analizar")
    texto = st.text_area("", height=200, placeholder="Escribe o pega aquí el texto...")
    if st.button("🔎 Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("⚠️ Ingresa algún texto.")

elif modo == "Archivo de texto":
    st.subheader("📂 Carga un archivo de texto")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo is not None:
        contenido = archivo.getvalue().decode("utf-8")
        with st.expander("👀 Ver contenido del archivo"):
            st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
        if st.button("📊 Analizar archivo"):
            with st.spinner("Analizando..."):
                resultados = procesar_texto(contenido)
                crear_visualizaciones(resultados)

# =========================
# INFO EXTRA
# =========================
with st.expander("📚 Información sobre el análisis"):
    st.markdown("""
    - **Sentimiento**: Varía de -1 (muy negativo) a 1 (muy positivo)  
    - **Subjetividad**: Varía de 0 (muy objetivo) a 1 (muy subjetivo)  
    """)

st.markdown("---")
st.markdown("🌙 Modo oscuro • Desarrollado con ❤️ usando Streamlit y TextBlob")

import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
import json
import streamlit.components.v1 as components  # <- para embeber lottie-web

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
    .stApp { background-color:#000000; color:#FFFFFF; }

    /* Títulos y textos */
    h1, h2, h3, h4, h5, h6 { color:#FFFFFF !important; }
    .stMarkdown, .stText, .stSubheader, .stHeader, .stTitle { color:#FFFFFF !important; }

    /* Labels */
    label, .stTextInput label, .stSelectbox label, .stTextArea label {
        color:#FFFFFF !important; font-weight:600;
    }

    /* Inputs */
    textarea, input, select {
        background-color:#1E1E1E !important; color:#FFFFFF !important;
        border:1px solid #555555 !important; border-radius:6px !important;
    }

    /* Botones */
    div.stButton > button {
        background-color:#1E1E1E; color:#FFFFFF; border:1px solid #FFFFFF;
        border-radius:8px; padding:.5em 1em; font-weight:700; transition:.3s;
    }
    div.stButton > button:hover { background-color:#FFFFFF; color:#000000; }

    /* Sidebar oscuro */
    section[data-testid="stSidebar"] { background-color:#111111 !important; color:#FFFFFF !important; }

    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color:#1E1E1E !important; color:#FFFFFF !important;
        border:1px solid #555555 !important; border-radius:6px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# ANIMACIÓN LOTTIE (sin fondo blanco con lottie-web)
# =========================
with open("crazy.json", "r", encoding="utf-8") as f:
    anim_text = json.dumps(json.load(f))

components.html(
    f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          html, body {{
            margin:0; padding:0; background:#000;     /* fondo negro dentro del iframe */
          }}
          #holder {{
            width:350px; height:350px; margin:0 auto;
            background:#000; border-radius:10px;      /* opcional */
          }}
        </style>
      </head>
      <body>
        <div id="holder"></div>
        <script src="https://unpkg.com/lottie-web@5.12.2/build/player/lottie.min.js"></script>
        <script>
          const animData = {anim_text};
          lottie.loadAnimation({{
            container: document.getElementById('holder'),
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: animData,
            rendererSettings: {{ preserveAspectRatio: 'xMidYMid meet', clearCanvas: true }}
          }});
        </script>
      </body>
    </html>
    """,
    height=380,
    scrolling=False
)

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
    stop_words = set(["a","de","la","the","and","to","in","of","que","y"])
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for p in palabras_filtradas:
        contador[p] = contador.get(p, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

translator = Translator()

def traducir_texto(texto):
    try:
        return translator.translate(texto, src="es", dest="en").text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_orig = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_trad = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    frases = [{"original": o, "traducido": t} for o, t in zip(frases_orig, frases_trad)]
    contador_palabras, palabras = contar_palabras(texto_ingles)
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Análisis de Sentimiento y Subjetividad")
        st.write("**Sentimiento:**")
        st.progress((resultados["sentimiento"] + 1) / 2)
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
            st.bar_chart(dict(list(resultados["contador_palabras"].items())[:10]))
    st.subheader("📜 Texto traducido")
    with st.expander("Ver traducción completa"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original (Español):**")
            st.text(resultados["texto_original"])
        with c2:
            st.markdown("**Traducido (Inglés):**")
            st.text(resultados["texto_traducido"])
    st.subheader("✂️ Frases detectadas")
    if resultados["frases"]:
        for i, f in enumerate(resultados["frases"][:10], 1):
            try:
                sent = TextBlob(f["traducido"]).sentiment.polarity
                emoji = "😊" if sent > 0.05 else "😟" if sent < -0.05 else "😐"
                st.write(f"{i}. {emoji} **Original:** *\"{f['original']}\"*")
                st.write(f"   **Traducción:** *\"{f['traducido']}\"* (Sentimiento: {sent:.2f})")
                st.write("---")
            except:
                st.write(f"{i}. **Original:** {f['original']}")
                st.write(f"   **Traducción:** {f['traducido']}")
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
                crear_visualizaciones(procesar_texto(texto))
        else:
            st.warning("⚠️ Ingresa algún texto.")
else:
    st.subheader("📂 Carga un archivo de texto")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo is not None:
        contenido = archivo.getvalue().decode("utf-8")
        with st.expander("👀 Ver contenido del archivo"):
            st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
        if st.button("📊 Analizar archivo"):
            with st.spinner("Analizando..."):
                crear_visualizaciones(procesar_texto(contenido))

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

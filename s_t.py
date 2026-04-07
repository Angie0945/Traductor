import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="🎤 Traductor por Voz",
    page_icon="🌍",
    layout="centered"
)

st.title("🎤 Traductor por Voz")
st.caption("Habla, traduce y escucha fácilmente 🌍🔊")

# ---------------- IMAGEN ----------------
image = Image.open('OIG7.jpg')
st.image(image, width=250)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Configuración")

    idiomas = {
        "Español": "es",
        "Inglés": "en",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Bengali": "bn"
    }

    in_lang = st.selectbox("🌐 Idioma de entrada", list(idiomas.keys()))
    out_lang = st.selectbox("🌍 Idioma de salida", list(idiomas.keys()))

    acentos = {
        "Default": "com",
        "EE.UU": "com",
        "Reino Unido": "co.uk",
        "Australia": "com.au"
    }

    tld = acentos[st.selectbox("🎙️ Acento", list(acentos.keys()))]

    mostrar_texto = st.checkbox("📄 Mostrar texto traducido")

# ---------------- BOTÓN GRABAR ----------------
st.subheader("🎤 Paso 1: Grabar voz")

stt_button = Button(label="🎤 Grabar (habla ahora)", width=250)

stt_button.js_on_event("button_click", CustomJS(code="""
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-ES';

    document.dispatchEvent(new CustomEvent("LISTENING", {detail: "start"}));

    recognition.onresult = function (e) {
        var text = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: text}));
    }

    recognition.onend = function() {
        document.dispatchEvent(new CustomEvent("LISTENING", {detail: "stop"}));
    }

    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,LISTENING",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ---------------- ESTADO ----------------
if result and "LISTENING" in result:
    if result["LISTENING"] == "start":
        st.info("🎙️ Te estoy escuchando...")
    elif result["LISTENING"] == "stop":
        st.success("✅ Grabación finalizada")

# ---------------- TEXTO DETECTADO ----------------
text = ""

if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.subheader("📝 Paso 2: Lo que dijiste")
    st.success(text)

# ---------------- TRADUCTOR ----------------
translator = Translator()

def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text

    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)

    if not os.path.exists("temp"):
        os.mkdir("temp")

    file_path = "temp/audio.mp3"
    tts.save(file_path)

    return file_path, trans_text

# ---------------- BOTÓN TRADUCIR ----------------
if text:
    st.subheader("🌍 Paso 3: Traducir")

    if st.button("🌍 Traducir texto"):

        with st.spinner("🔄 Traduciendo..."):
            audio_path, output_text = text_to_speech(
                idiomas[in_lang],
                idiomas[out_lang],
                text,
                tld
            )

        st.subheader("📄 Traducción")
        st.success(output_text)

        st.subheader("🔊 Paso 4: Escuchar resultado")
        st.audio(audio_path)

        if mostrar_texto:
            st.info(output_text)

# ---------------- LIMPIEZA ----------------
def remove_files():
    files = glob.glob("temp/*.mp3")
    now = time.time()
    for f in files:
        if os.stat(f).st_mtime < now - 86400:
            os.remove(f)

remove_files()

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("✨ Hecho con Streamlit + Voz + IA")


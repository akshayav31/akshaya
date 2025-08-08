import streamlit as st
import wikipedia
import speech_recognition as sr
import pyttsx3
import cv2
import numpy as np
import pandas as pd
import qrcode
import datetime
from PIL import Image
from pyzbar.pyzbar import decode
import tempfile
import os

# Initialize TTS engine
tts = pyttsx3.init()

# Set app configuration
st.set_page_config(page_title="All-in-One Tool", layout="centered")
st.title("🤖 Wikipedia Bot + 📷 QR Tools + 🧹 Cache Clear")

# Dark mode toggle
dark_mode = st.toggle("🌗 Dark Mode")
if dark_mode:
    st.markdown("<style>body { background-color: #1e1e1e; color: white; }</style>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📚 Wiki Chatbot", "📷 QR Scanner", "🧾 QR Generator"])

# -------------------------------
# TAB 1: Wikipedia Chatbot
# -------------------------------
with tab1:
    st.subheader("Wikipedia Chatbot 🤖")

    # Language selection
    lang = st.selectbox("Choose Wikipedia language", ["en", "hi", "ta", "kn", "fr", "de"])
    wikipedia.set_lang(lang)

    # Voice or text input
    input_mode = st.radio("Input Method", ["Text", "Voice"])

    if input_mode == "Text":
        query = st.text_input("Enter your question:")
    else:
        if st.button("🎙️ Record Voice"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening...")
                audio = recognizer.listen(source, timeout=5)
                try:
                    query = recognizer.recognize_google(audio, language=lang)
                    st.success(f"You said: {query}")
                except sr.UnknownValueError:
                    query = ""
                    st.error("Sorry, could not understand.")
                except:
                    query = ""
                    st.error("Error during voice recognition.")

    if st.button("🔍 Search Wikipedia") and query:
        try:
            result = wikipedia.summary(query, sentences=2)
            st.success(result)
            tts.say(result)
            tts.runAndWait()
        except wikipedia.exceptions.DisambiguationError as e:
            st.warning("Too many options, try to be more specific.")
        except:
            st.error("No result found.")

# -------------------------------
# TAB 2: QR Scanner
# -------------------------------
with tab2:
    st.subheader("QR Code Scanner 📷")
    method = st.radio("Choose method:", ["Webcam", "Upload Image"])

    def save_qr(data):
        file = "qr_scan_log.csv"
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df = pd.DataFrame([[data, now]], columns=["Data", "Timestamp"])
        if os.path.exists(file):
            df.to_csv(file, mode='a', header=False, index=False)
        else:
            df.to_csv(file, index=False)

    if method == "Webcam":
        if st.checkbox("Start Webcam"):
            FRAME_WINDOW = st.image([])
            cap = cv2.VideoCapture(0)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                decoded_objs = decode(frame)
                for obj in decoded_objs:
                    data = obj.data.decode("utf-8")
                    st.success(f"QR Code: {data}")
                    save_qr(data)
                    cap.release()
                    FRAME_WINDOW.empty()
                    st.stop()

                FRAME_WINDOW.image(frame, channels="BGR")

    elif method == "Upload Image":
        uploaded_img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="Uploaded QR Image")
            decoded_objs = decode(img)
            if decoded_objs:
                for obj in decoded_objs:
                    data = obj.data.decode("utf-8")
                    st.success(f"QR Code: {data}")
                    save_qr(data)
            else:
                st.warning("No QR code found.")

    with st.expander("📄 QR Scan History"):
        try:
            df = pd.read_csv("qr_scan_log.csv")
            st.dataframe(df)
        except:
            st.info("No scan data available.")

    if st.button("🧹 Clear QR Scan History"):
        if os.path.exists("qr_scan_log.csv"):
            os.remove("qr_scan_log.csv")
            st.success("Scan history cleared.")

# -------------------------------
# TAB 3: QR Generator
# -------------------------------
with tab3:
    st.subheader("QR Code Generator 🧾")
    qr_data = st.text_input("Enter text to encode in QR:")

    if st.button("Generate QR"):
        qr_img = qrcode.make(qr_data)
        st.image(qr_img, caption="Your QR Code")

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr_img.save(temp.name)
        with open(temp.name, "rb") as f:
            st.download_button("⬇️ Download QR", f, file_name="qr_code.png")

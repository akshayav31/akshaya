import streamlit as st
import wikipedia
import speech_recognition as sr
import tempfile
import os
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode

st.set_page_config(page_title="Chatbot + QR Scanner", layout="centered")
st.markdown(
    """
    <style>
    .glow-icon {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: url('https://cdn-icons-png.flaticon.com/512/4712/4712039.png') no-repeat center/cover;
        box-shadow: 0 0 20px #00ffcc, 0 0 30px #00ffcc, 0 0 40px #00ffcc;
        animation: pulse 2s infinite;
        margin: auto;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 20px #00ffcc; }
        50% { box-shadow: 0 0 40px #00ffcc; }
        100% { box-shadow: 0 0 20px #00ffcc; }
    }
    </style>
    <div class="glow-icon"></div>
    """,
    unsafe_allow_html=True
)
st.title("🤖 Chatbot + 📷 QR Code Scanner")


# Tabs (add third tab)
tab1, tab2, tab3 = st.tabs(["📚 Wikipedia Chatbot", "📷 QR Code Scanner", "ℹ️ About Us"])

# --- TAB 1: Wikipedia Chatbot ---
with tab1:
    st.subheader("Ask anything. Type or speak!")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Function: Get Wikipedia summary
    def get_wikipedia_summary(query):
        try:
            results = wikipedia.search(query)
            if not results:
                return "❌ Sorry, no results found."
            summary = wikipedia.summary(results[0], sentences=2, auto_suggest=False, redirect=True)
            return summary
        except wikipedia.DisambiguationError as e:
            return f"⚠️ Too broad. Did you mean: {', '.join(e.options[:5])}?"
        except wikipedia.PageError:
            return "❌ Page not found."
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # 🔠 Text input
    user_input = st.text_input("Type your question here:")

    # 🎤 Voice input (upload)
    audio_file = st.file_uploader("🎤 Or upload your voice question (WAV format)", type=["wav"])

    # Process voice file
    if audio_file is not None:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_filename = tmp_file.name

        with sr.AudioFile(tmp_filename) as source:
            audio_data = recognizer.record(source)
            try:
                user_input = recognizer.recognize_google(audio_data)
                st.success(f"You said: {user_input}")
            except sr.UnknownValueError:
                st.error("Sorry, could not understand your voice.")
            except sr.RequestError:
                st.error("Could not connect to speech recognition service.")

        os.remove(tmp_filename)

    # Respond if input exists
    if user_input:
        response = get_wikipedia_summary(user_input)
        st.session_state.chat_history.append((user_input, response))

    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Chat History")
        for idx, (user, bot) in enumerate(reversed(st.session_state.chat_history), 1):
            st.markdown(f"**🧑 You {idx}:** {user}")
            st.markdown(f"**🤖 Bot {idx}:** {bot}")
            st.markdown("---")

        # 🧹 Clear history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history.clear()
            st.success("Chat history cleared!")

# --- TAB 2: QR Code Scanner ---
with tab2:
    st.subheader("📷 Upload a QR Code Image to Scan")

    uploaded_file = st.file_uploader("Upload QR image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded QR Code", use_column_width=True)

        # Decode
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        decoded_objs = decode(img_cv)

        if decoded_objs:
            for obj in decoded_objs:
                data = obj.data.decode("utf-8")
                st.success(f"🔓 Decoded Data: {data}")
        else:
            st.warning("⚠️ No QR code detected.")
            # --- TAB 3: About Us ---
with tab3:
    st.subheader("About Us")
    st.markdown("""
    ### Welcome to Chatbot + QR Scanner!

    This app combines two handy tools into one interface:

    - 🤖 **Wikipedia Chatbot**: Ask questions by typing or uploading your voice! Powered by Wikipedia API and speech recognition.
    - 📷 **QR Code Scanner**: Upload images containing QR codes and get the decoded information instantly.

    ---
    **Developed by:**  
    AKSHAYA V, DHARSHINI J, HARSHITHA B.M, SRIMATHI K
                
                            

    **Contact:**  
    - Email: dharshudharshu148@gmail.com, 
             acquireness@gmail.com      
    - Website: [https://yourwebsite.com](https://yourwebsite.com)

    ---
    Thank you for using our app! Feel free to contribute or suggest features.
    """)
# Project Link
    st.subheader("🔗 Link of the Project")
    st.markdown("[Click here to view the project](https://your-project-link.com)")

    # Snapshots Section
    st.subheader("🖼️ Snapshots of the Project")

    SNAPSHOT_DIR = "snapshots"
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    uploaded_files = st.file_uploader("Upload snapshots (only once)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            file_path = os.path.join(SNAPSHOT_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.success("✅ Files uploaded successfully!")

    saved_files = os.listdir(SNAPSHOT_DIR)
    if saved_files:
        st.markdown("### Saved Snapshots:")
        for fname in saved_files:
            fpath = os.path.join(SNAPSHOT_DIR, fname)
            st.image(fpath, use_column_width=True)
    else:
        st.info("No snapshots uploaded yet.")
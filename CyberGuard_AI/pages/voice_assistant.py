
import streamlit as st
from cyberguard.voice_assistant import (
    listen,
    speak,
    get_response
)

def render(results):
    st.title("🎙️ CyberGuard Voice Assistant")

    st.write(
        "Your AI cybersecurity assistant. "
        "Ask questions about threats and reports."
    )

    question = st.text_input(
        "Ask CyberGuard",
        placeholder="Give me the security summary..."
    )

    st.subheader("Voice Interaction")

    spoken = listen()

    command = spoken or question

    if spoken:
        st.success(f"You said: {spoken}")

    if st.button("Get Answer") and command:
        answer = get_response(command, results)

        st.info(answer)

        audio = speak(answer)

        if audio:
            st.audio(audio, format="audio/mp3")

    with st.expander("Example questions"):
        st.write("Explain phishing")
        st.write("What is ransomware?")
        st.write("Give me the security summary")
        st.write("Explain the system workflow")

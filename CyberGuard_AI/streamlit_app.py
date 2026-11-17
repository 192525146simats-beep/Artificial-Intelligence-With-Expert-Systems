
import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

# Optional visual floating panel
try:
    from streamlit_float import float_init
    FLOAT_AVAILABLE = True
except ImportError:
    FLOAT_AVAILABLE = False

# Voice recording
try:
    from streamlit_mic_recorder import mic_recorder
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False

# Groq AI
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# ---------------------------------------------------------
# APPLICATION CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="CyberGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSET_DIR / "logo.png"

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #061426, #0a1d33);
    color: #edf7ff;
}
[data-testid="stSidebar"] {
    background: #09182a;
    border-right: 1px solid #193b58;
}
h1, h2, h3 {
    color: #e9f7ff;
}
p, label {
    color: #c0d5e7;
}
.metric-card {
    background: #102942;
    border: 1px solid #205273;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
}
.metric-number {
    color: #28d8ff;
    font-size: 30px;
    font-weight: 700;
}
.small-muted {
    color: #9db8ce;
    font-size: 13px;
}
.hero {
    padding: 22px;
    border-radius: 14px;
    background: linear-gradient(110deg, #103653, #09233b);
    border: 1px solid #1d5877;
    margin-bottom: 20px;
}
div[data-testid="stMetric"] {
    background: #102942;
    border: 1px solid #205273;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# GROQ SECRET CONFIGURATION
# ---------------------------------------------------------

def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]

        if "groq" in st.secrets:
            return st.secrets["groq"]["api_key"]
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


def get_groq_client():
    key = get_groq_key()

    if not key:
        return None

    if not GROQ_AVAILABLE:
        return None

    return Groq(api_key=key)


# ---------------------------------------------------------
# SAMPLE DATA
# Replace this with your real security-event dataset later.
# ---------------------------------------------------------

def get_events():
    return pd.DataFrame([
        {
            "IP Address": "192.168.1.10",
            "Threat": "Brute Force",
            "Severity": "High",
            "Status": "Detected",
            "Failed Logins": 35,
            "Requests": 120
        },
        {
            "IP Address": "192.168.1.15",
            "Threat": "DDoS",
            "Severity": "Critical",
            "Status": "Under Review",
            "Failed Logins": 2,
            "Requests": 950
        },
        {
            "IP Address": "192.168.1.22",
            "Threat": "Port Scanning",
            "Severity": "Medium",
            "Status": "Detected",
            "Failed Logins": 5,
            "Requests": 250
        },
        {
            "IP Address": "192.168.1.30",
            "Threat": "Suspicious Login",
            "Severity": "High",
            "Status": "Investigating",
            "Failed Logins": 18,
            "Requests": 90
        },
        {
            "IP Address": "192.168.1.45",
            "Threat": "Normal Traffic",
            "Severity": "Low",
            "Status": "Safe",
            "Failed Logins": 0,
            "Requests": 20
        }
    ])


# ---------------------------------------------------------
# SHARED SESSION STATE
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_voice_reply" not in st.session_state:
    st.session_state.last_voice_reply = ""


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

def dashboard():

    st.markdown("""
    <div class="hero">
        <h1>🛡️ CyberGuard AI</h1>
        <h3>Intelligent Cyber Threat Analysis Expert System</h3>
        <p>AI-powered cybersecurity monitoring and threat awareness.</p>
    </div>
    """, unsafe_allow_html=True)

    df = get_events()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Security Events", len(df))
    c2.metric("Critical Threats", len(df[df["Severity"] == "Critical"]))
    c3.metric("High Risk", len(df[df["Severity"] == "High"]))
    c4.metric("Safe Events", len(df[df["Severity"] == "Low"]))

    st.subheader("Security Event Overview")

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Threat Distribution")

    counts = df["Threat"].value_counts()
    st.bar_chart(counts)

    st.info(
        "The displayed records are sample demonstration data. "
        "Connect your actual security dataset for real analysis."
    )


# ---------------------------------------------------------
# THREAT ANALYSIS
# ---------------------------------------------------------

def threat_analysis():

    st.title("🔍 Threat Analysis")
    st.write("Review suspicious cybersecurity events.")

    df = get_events()

    severity = st.selectbox(
        "Filter by severity",
        ["All", "Critical", "High", "Medium", "Low"]
    )

    if severity != "All":
        df = df[df["Severity"] == severity]

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Analyse an event")

    ip = st.text_input("IP Address", "192.168.1.100")
    failed = st.number_input("Failed login attempts", 0, 10000, 10)
    requests = st.number_input("Number of requests", 0, 100000, 200)

    if st.button("Analyse Event", type="primary"):

        if failed > 30 or requests > 800:
            st.error("High-risk activity detected.")
            st.write("Recommendation: Investigate the source and review access logs.")

        elif failed > 10 or requests > 300:
            st.warning("Suspicious activity detected.")
            st.write("Recommendation: Monitor the IP address and verify user activity.")

        else:
            st.success("No strong threat indicator found in this demonstration.")

        st.caption("This is a demonstration rule, not a validated security verdict.")


# ---------------------------------------------------------
# THREAT INTELLIGENCE
# ---------------------------------------------------------

def threat_intelligence():

    st.title("🌐 Threat Intelligence")

    st.write(
        "Understand common cyberattack patterns and their indicators."
    )

    threats = {
        "DDoS Attack": (
            "An attacker floods a service with traffic to make it unavailable.",
            "Unusual traffic spikes, repeated requests and service degradation.",
            "Use traffic filtering, rate limits and DDoS protection."
        ),
        "Brute Force": (
            "Repeated password attempts are used to gain unauthorized access.",
            "Many failed logins from the same source.",
            "Apply MFA, account lockouts and login monitoring."
        ),
        "Port Scanning": (
            "An attacker checks open network ports to identify services.",
            "Repeated connection attempts across multiple ports.",
            "Restrict exposed ports and monitor firewall logs."
        ),
        "Phishing": (
            "Fraudulent messages attempt to steal credentials or sensitive data.",
            "Suspicious links, unexpected attachments and fake login pages.",
            "Use email filtering and user awareness training."
        ),
        "Malware": (
            "Malicious software attempts to damage, monitor or control systems.",
            "Unexpected processes, suspicious files and unusual network traffic.",
            "Use endpoint protection and isolate affected systems."
        )
    }

    for name, details in threats.items():
        with st.expander(name):
            st.write("**Description:**", details[0])
            st.write("**Indicators:**", details[1])
            st.write("**Recommended action:**", details[2])


# ---------------------------------------------------------
# EXPERT SYSTEM
# ---------------------------------------------------------

def expert_system():

    st.title("🧩 Cybersecurity Expert System")

    st.write("Evaluate activity using a demonstration rule base.")

    failed = st.number_input(
        "Failed login attempts",
        min_value=0,
        max_value=10000,
        value=5,
        key="expert_failed"
    )

    traffic = st.number_input(
        "Requests per minute",
        min_value=0,
        max_value=100000,
        value=100,
        key="expert_traffic"
    )

    unknown_port = st.checkbox("Unknown or suspicious port detected")
    unusual_time = st.checkbox("Login at an unusual time")

    if st.button("Run Expert Rules", type="primary"):

        findings = []

        if failed >= 20:
            findings.append(
                "Rule 1: Repeated failed logins indicate possible brute-force activity."
            )

        if traffic >= 800:
            findings.append(
                "Rule 2: High traffic volume may indicate a DDoS pattern."
            )

        if unknown_port:
            findings.append(
                "Rule 3: Unknown port usage requires investigation."
            )

        if unusual_time:
            findings.append(
                "Rule 4: Unusual login time requires identity verification."
            )

        if findings:
            st.warning("Expert system alerts")
            for item in findings:
                st.write("•", item)
        else:
            st.success("No demonstration rules were triggered.")

        st.caption(
            "These are educational rules. Validate findings using real logs."
        )


# ---------------------------------------------------------
# AI PREDICTION
# ---------------------------------------------------------

def ai_prediction():

    st.title("🤖 AI Threat Prediction")

    st.write(
        "Enter event details to estimate a demonstration risk score."
    )

    failed = st.slider(
        "Failed login attempts",
        0, 100, 5
    )

    traffic = st.slider(
        "Network requests",
        0, 2000, 100
    )

    port = st.selectbox(
        "Port category",
        ["Normal", "Unusual", "Unknown"]
    )

    if st.button("Predict Threat", type="primary"):

        # Transparent demonstration score.
        # Replace with your trained model once its feature schema is confirmed.
        score = min(
            100,
            failed * 1.5
            + traffic * 0.035
            + (25 if port == "Unusual" else 40 if port == "Unknown" else 0)
        )

        st.metric("Estimated Risk Score", f"{score:.1f}%")
        st.progress(int(score))

        if score >= 70:
            st.error("High demonstration risk")
            st.write("Recommendation: Investigate the event immediately.")

        elif score >= 40:
            st.warning("Moderate demonstration risk")
            st.write("Recommendation: Monitor the activity.")

        else:
            st.success("Low demonstration risk")
            st.write("Recommendation: Continue normal monitoring.")

        st.caption(
            "Important: This is a rule-based demonstration score, "
            "not a prediction from your trained threat_model.pkl."
        )


# ---------------------------------------------------------
# SYSTEM WORKFLOW
# ---------------------------------------------------------

def workflow():

    st.title("🔄 System Workflow")

    steps = [
        "1. Security Event Input",
        "2. Data Cleaning and Preprocessing",
        "3. Feature Extraction",
        "4. Machine Learning Threat Prediction",
        "5. Expert Rule Evaluation",
        "6. Threat Classification",
        "7. Security Recommendations",
        "8. Dashboard and Reports"
    ]

    for step in steps:
        st.info(step)

    st.subheader("System Architecture")

    st.graphviz_chart("""
    digraph CyberGuard {
        rankdir=TB;
        node [shape=box, style=rounded, color="#16BCEB"];

        A [label="Security Event Input"];
        B [label="Data Preprocessing"];
        C [label="Feature Extraction"];
        D [label="Machine Learning"];
        E [label="Expert Rule Engine"];
        F [label="Threat Classification"];
        G [label="Recommendations"];
        H [label="Dashboard and Reports"];

        A -> B -> C;
        C -> D;
        C -> E;
        D -> F;
        E -> F;
        F -> G -> H;
    }
    """)


# ---------------------------------------------------------
# REPORTS
# ---------------------------------------------------------

def reports():

    st.title("📈 Security Reports")

    df = get_events()

    st.subheader("Event Report")

    st.dataframe(df, use_container_width=True)

    st.subheader("Severity Summary")

    summary = df.groupby("Severity").size().reset_index(name="Events")

    st.dataframe(summary, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Security Report CSV",
        data=csv,
        file_name="cyberguard_security_report.csv",
        mime="text/csv"
    )


# ---------------------------------------------------------
# VOICE ASSISTANT PAGE
# ---------------------------------------------------------

def voice_assistant_page():

    st.title("🎙️ CyberGuard Voice Assistant")

    st.write(
        "Ask cybersecurity questions using your microphone "
        "or type your question."
    )

    st.info(
        "Press Start recording, speak, and press Stop recording. "
        "The assistant will transcribe and answer your question."
    )

    if not MIC_AVAILABLE:
        st.error("Microphone package is not installed.")
        return

    if not get_groq_key():
        st.error("Please configure your Groq API key in Streamlit Secrets.")
        return

    audio = mic_recorder(
        start_prompt="🎙️ Start recording",
        stop_prompt="⏹️ Stop recording",
        just_once=True,
        use_container_width=True,
        key="main_voice_recorder"
    )

    if audio and audio.get("bytes"):

        client = get_groq_client()

        if client is None:
            st.error("Groq client is unavailable.")
            return

        try:
            with st.spinner("Transcribing your voice..."):

                transcription = client.audio.transcriptions.create(
                    file=(
                        "cyberguard_voice.wav",
                        audio["bytes"],
                        "audio/wav"
                    ),
                    model="whisper-large-v3-turbo"
                )

                question = transcription.text.strip()

            st.write("**You said:**", question)

            if question:
                answer = ask_groq(question)

                if answer:
                    st.session_state.messages.append(
                        {"role": "user", "content": question}
                    )
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                    st.markdown("### CyberGuard AI Response")
                    st.write(answer)

                    play_female_voice(answer)

        except Exception as e:
            st.error(f"Voice processing failed: {e}")

    st.divider()

    typed_question = st.text_input(
        "Or type your question",
        key="voice_text_question"
    )

    if st.button("Ask CyberGuard AI") and typed_question.strip():

        answer = ask_groq(typed_question.strip())

        if answer:
            st.write(answer)
            play_female_voice(answer)


# ---------------------------------------------------------
# GROQ CHAT RESPONSE
# ---------------------------------------------------------

def ask_groq(question):

    client = get_groq_client()

    if client is None:
        st.error(
            "Groq API key is missing or the Groq package is unavailable."
        )
        return None

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CyberGuard AI, a helpful cybersecurity "
                        "assistant. Explain threats, security events, "
                        "network risks, defensive controls and safe "
                        "incident response in clear, simple language. "
                        "Never claim that sample data proves a real attack. "
                        "Do not provide instructions for unauthorized access."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.4,
            max_tokens=600
        )

        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Groq chat error: {e}")
        return None


# ---------------------------------------------------------
# FEMALE TEXT-TO-SPEECH
# ---------------------------------------------------------

def play_female_voice(text):

    client = get_groq_client()

    if client is None:
        return

    try:
        # Orpheus English TTS has a 200-character input limit.
        spoken_text = text[:200]

        with st.spinner("Generating female voice..."):

            response = client.audio.speech.create(
                model="canopylabs/orpheus-v1-english",
                voice="hannah",
                input=spoken_text,
                response_format="wav"
            )

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as temp_file:

                temp_path = temp_file.name

            response.write_to_file(temp_path)

            with open(temp_path, "rb") as file:
                audio_bytes = file.read()

            os.remove(temp_path)

        st.audio(audio_bytes, format="audio/wav")

        if len(text) > 200:
            st.caption(
                "Only the first 200 characters were spoken. "
                "The complete answer is displayed above."
            )

    except Exception as e:
        st.warning(
            "Female voice generation is unavailable. "
            "Check Groq TTS model access and usage limits. "
            f"Details: {e}"
        )


# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------

pages = {
    "MAIN": [
        st.Page(
            dashboard,
            title="Dashboard",
            icon="🏠",
            default=True
        ),
    ],
    "THREAT MANAGEMENT": [
        st.Page(
            threat_analysis,
            title="Threat Analysis",
            icon="🔍"
        ),
        st.Page(
            threat_intelligence,
            title="Threat Intelligence",
            icon="🌐"
        ),
        st.Page(
            expert_system,
            title="Expert System",
            icon="🧩"
        ),
        st.Page(
            ai_prediction,
            title="AI Prediction",
            icon="🤖"
        ),
    ],
    "SYSTEM": [
        st.Page(
            workflow,
            title="System Workflow",
            icon="🔄"
        ),
        st.Page(
            reports,
            title="Security Reports",
            icon="📊"
        ),
        st.Page(
            voice_assistant_page,
            title="Voice Assistant",
            icon="🎙️"
        ),
    ]
}

if FLOAT_AVAILABLE:
    try:
        float_init()
    except Exception:
        pass

current_page = st.navigation(pages, position="sidebar")

# Run selected page
current_page.run()


# ---------------------------------------------------------
# FLOATING VOICE ASSISTANT - SHARED ON EVERY PAGE
# ---------------------------------------------------------

assistant_box = st.container()

if FLOAT_AVAILABLE:
    try:
        assistant_box.float(
            "bottom: 1rem; right: 1rem; "
            "width: 340px; z-index: 999;"
        )
    except Exception:
        pass

with assistant_box:

    with st.expander("🎙️ CyberGuard AI Assistant", expanded=False):

        st.caption("Your cybersecurity voice assistant")

        if not get_groq_key():
            st.warning("Configure your Groq API key to activate AI.")
        else:

            if MIC_AVAILABLE:

                floating_audio = mic_recorder(
                    start_prompt="🎙️ Speak",
                    stop_prompt="⏹️ Stop",
                    just_once=True,
                    use_container_width=True,
                    key="floating_voice_recorder"
                )

                if floating_audio and floating_audio.get("bytes"):

                    try:
                        client = get_groq_client()

                        with st.spinner("Listening and understanding..."):

                            transcription = client.audio.transcriptions.create(
                                file=(
                                    "question.wav",
                                    floating_audio["bytes"],
                                    "audio/wav"
                                ),
                                model="whisper-large-v3-turbo"
                            )

                            question = transcription.text.strip()

                        st.write("You:", question)

                        if question:
                            answer = ask_groq(question)

                            if answer:
                                st.write("CyberGuard:", answer)
                                play_female_voice(answer)

                    except Exception as e:
                        st.error(f"Voice error: {e}")

            floating_text = st.text_input(
                "Ask CyberGuard AI",
                key="floating_chat_input"
            )

            if st.button(
                "Send",
                key="floating_send_button",
                use_container_width=True
            ) and floating_text.strip():

                answer = ask_groq(floating_text.strip())

                if answer:
                    st.write(answer)
                    play_female_voice(answer)

            st.caption(
                "Microphone access begins only after you press Speak."
            )


# ---------------------------------------------------------
# SIDEBAR FOOTER
# ---------------------------------------------------------

with st.sidebar:

    st.divider()

    st.caption("CYBERGUARD AI")
    st.caption("Intelligent Cyber Threat Analysis")
    st.caption("Academic AI & Expert Systems Project")

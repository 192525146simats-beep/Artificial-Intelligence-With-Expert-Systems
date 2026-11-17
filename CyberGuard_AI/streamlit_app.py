
import os
import random
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from groq import Groq
from gtts import gTTS


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="CyberGuard AI | Intelligent Cyber Threat Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CHAT_MODEL = "openai/gpt-oss-120b"
STT_MODEL = "whisper-large-v3-turbo"


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 5%, #132b50 0%, transparent 28%),
        linear-gradient(135deg, #07111f, #0b1729 55%, #101d32);
    color: #edf4ff;
}

header[data-testid="stHeader"] {
    background: rgba(7,17,31,.85);
}

section[data-testid="stSidebar"] {
    background: #0b1627;
    min-width: 270px !important;
    max-width: 290px !important;
    width: 290px !important;
    border-right: 1px solid #203651;
    overflow-x: hidden !important;
    overflow-y: auto !important;
}

section[data-testid="stSidebar"] > div {
    width: 100%;
    overflow-x: hidden;
}

.hero {
    padding: 28px;
    border-radius: 20px;
    background: linear-gradient(120deg, #112d50, #173d68, #10243f);
    border: 1px solid #31557b;
    margin-bottom: 22px;
    box-shadow: 0 12px 35px rgba(0,0,0,.22);
}

.hero h1 {
    color: white;
    font-size: 32px;
    font-weight: 800;
}

.hero p {
    color: #c3d8f2;
}

.metric-card {
    background: linear-gradient(145deg, #142b47, #102139);
    border: 1px solid #294563;
    border-radius: 16px;
    padding: 18px;
    min-height: 105px;
    transition: transform .2s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: #42a5ff;
}

.metric-label {
    color: #9db6d4;
    font-size: 13px;
}

.metric-value {
    color: white;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

.panel {
    background: #102139;
    border: 1px solid #294563;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
}

.status-online {
    color: #6ee7b7;
    font-weight: 700;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid #347fc0;
    background: linear-gradient(90deg, #1768b0, #2488d8);
    color: white;
    font-weight: 700;
    min-height: 42px;
}

div.stButton > button:hover {
    border-color: #79c5ff;
    color: white;
}

.stChatMessage {
    background: #12263f;
    border: 1px solid #294563;
    border-radius: 14px;
}

footer {
    visibility: hidden;
}

@media(max-width:800px) {
    section[data-testid="stSidebar"] {
        min-width: 250px !important;
        max-width: 250px !important;
        width: 250px !important;
    }
    .hero h1 {
        font-size: 25px;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# GROQ API CONFIGURATION
# ==========================================================

def get_api_key():
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return os.getenv("GROQ_API_KEY", "")


@st.cache_resource
def get_groq_client():
    key = get_api_key()
    if not key:
        return None
    return Groq(api_key=key)


client = get_groq_client()


# ==========================================================
# DEMONSTRATION THREAT DATA
# ==========================================================

@st.cache_data
def create_demo_data():
    random.seed(42)

    threat_types = [
        "Malware",
        "Phishing",
        "Brute Force",
        "DDoS",
        "SQL Injection",
        "Suspicious Login",
        "Ransomware",
        "Port Scanning",
    ]

    statuses = [
        "Blocked",
        "Investigating",
        "Resolved",
        "Monitoring",
    ]

    records = []

    for i in range(120):
        risk = round(random.uniform(5, 99), 1)

        if risk >= 85:
            severity = "Critical"
        elif risk >= 65:
            severity = "High"
        elif risk >= 35:
            severity = "Medium"
        else:
            severity = "Low"

        records.append({
            "Event ID": f"CG-{1000+i}",
            "Timestamp": datetime.now() - timedelta(
                minutes=random.randint(1, 10000)
            ),
            "Source IP": (
                f"{random.randint(10,220)}."
                f"{random.randint(1,254)}."
                f"{random.randint(1,254)}."
                f"{random.randint(1,254)}"
            ),
            "Threat Type": random.choice(threat_types),
            "Severity": severity,
            "Risk Score": risk,
            "Status": random.choice(statuses),
        })

    return pd.DataFrame(records)


df = create_demo_data()


# ==========================================================
# COMMON FUNCTIONS
# ==========================================================

def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <span class="status-online">● CYBERGUARD SYSTEM ACTIVE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# AI CHAT FUNCTION
# ==========================================================

SYSTEM_PROMPT = """
You are CyberGuard AI, a cybersecurity analysis assistant.

Help users understand:
- Malware and ransomware
- Phishing attacks
- Brute-force attacks
- DDoS attacks
- SQL injection
- Suspicious login activity
- Cybersecurity incident response
- Defensive security recommendations

Give clear, practical and ethical defensive guidance.
Do not claim to have scanned a real network.
"""


def ask_groq(question, history=None):
    if client is None:
        return (
            "GROQ_API_KEY is missing. Add your Groq API key "
            "in Streamlit Cloud Secrets."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-8:])

    messages.append({
        "role": "user",
        "content": question,
    })

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_completion_tokens=1400,
        )
        return response.choices[0].message.content or "No response received."

    except Exception as exc:
        return f"AI chat error: {str(exc)}"


# ==========================================================
# AUDIO GENERATION USING gTTS
# ==========================================================

def generate_audio(text):
    """
    Generate an MP3 audio response using gTTS.
    No Groq TTS model or Orpheus terms acceptance is required.
    """

    clean_text = str(text).strip()

    if not clean_text:
        raise ValueError("There is no response text to convert to audio.")

    # Keep the request at a manageable length.
    if len(clean_text) > 3500:
        clean_text = clean_text[:3500]

    audio_buffer = BytesIO()

    tts = gTTS(
        text=clean_text,
        lang="en",
        slow=False,
    )

    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    return audio_buffer.getvalue()


# ==========================================================
# DASHBOARD
# ==========================================================

def dashboard_page():
    hero(
        "CyberGuard AI",
        "Intelligent Cyber Threat Analysis Expert System",
    )

    metrics = [
        ("Total Events", len(df)),
        ("Critical Threats", int((df["Severity"] == "Critical").sum())),
        ("High Threats", int((df["Severity"] == "High").sum())),
        ("Blocked Events", int((df["Status"] == "Blocked").sum())),
        ("Average Risk", f"{df['Risk Score'].mean():.1f}%"),
    ]

    cols = st.columns(5)

    for col, (label, value) in zip(cols, metrics):
        with col:
            metric_card(label, value)

    st.write("")

    left, right = st.columns(2)

    with left:
        st.subheader("Threat Distribution")

        counts = df["Threat Type"].value_counts().reset_index()
        counts.columns = ["Threat Type", "Count"]

        fig = px.pie(
            counts,
            names="Threat Type",
            values="Count",
            hole=0.55,
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Severity Overview")

        counts = (
            df["Severity"]
            .value_counts()
            .reindex(["Critical", "High", "Medium", "Low"], fill_value=0)
            .reset_index()
        )
        counts.columns = ["Severity", "Count"]

        fig = px.bar(
            counts,
            x="Severity",
            y="Count",
            color="Severity",
            text="Count",
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Threat Events")

    st.dataframe(
        df.sort_values("Timestamp", ascending=False).head(12),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "These are generated demonstration records, not live network events."
    )


# ==========================================================
# THREAT ANALYSIS
# ==========================================================

def threat_analysis_page():
    hero(
        "Threat Analysis",
        "Evaluate suspicious activity using an illustrative risk calculation.",
    )

    with st.form("analysis_form"):
        activity = st.text_area("Describe the suspicious activity")

        failed_logins = st.slider(
            "Failed login attempts",
            0, 100, 5,
        )

        traffic = st.selectbox(
            "Network traffic pattern",
            ["Normal", "Unusual", "Very High"],
        )

        suspicious_file = st.selectbox(
            "Suspicious file detected?",
            ["No", "Yes"],
        )

        external_access = st.selectbox(
            "Unauthorised external access?",
            ["No", "Yes"],
        )

        submitted = st.form_submit_button(
            "Analyse Threat",
            use_container_width=True,
        )

    if submitted:
        score = min(
            100,
            failed_logins * 0.8
            + {"Normal": 5, "Unusual": 25, "Very High": 40}[traffic]
            + (25 if suspicious_file == "Yes" else 0)
            + (25 if external_access == "Yes" else 0),
        )

        level = (
            "CRITICAL" if score >= 80 else
            "HIGH" if score >= 60 else
            "MEDIUM" if score >= 30 else
            "LOW"
        )

        st.metric("Illustrative Risk Score", f"{score:.1f}/100")
        st.progress(int(score))
        st.subheader(f"Risk Level: {level}")

        if level in ("CRITICAL", "HIGH"):
            st.error("Recommended action: Investigate immediately.")
        elif level == "MEDIUM":
            st.warning("Recommended action: Monitor and investigate.")
        else:
            st.success("Recommended action: Continue routine monitoring.")

        if activity.strip():
            st.write("Activity submitted:", activity)

    st.caption(
        "This is a demonstration score, not a validated detection engine."
    )


# ==========================================================
# THREAT INTELLIGENCE
# ==========================================================

def threat_intelligence_page():
    hero(
        "Threat Intelligence",
        "Explore sample threat indicators and event classifications.",
    )

    search = st.text_input("Search threat records")

    filtered = df.copy()

    if search:
        mask = filtered.astype(str).apply(
            lambda col: col.str.contains(search, case=False, na=False)
        ).any(axis=1)
        filtered = filtered[mask]

    st.write(f"Records found: {len(filtered)}")

    st.dataframe(
        filtered.sort_values("Risk Score", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.caption("The records shown are synthetic demonstration indicators.")


# ==========================================================
# EXPERT SYSTEM
# ==========================================================

def expert_system_page():
    hero(
        "Cybersecurity Expert System",
        "Rule-based threat interpretation and defensive recommendations.",
    )

    threat = st.selectbox(
        "Select detected threat",
        [
            "Phishing",
            "Malware",
            "Ransomware",
            "Brute Force",
            "DDoS",
            "SQL Injection",
            "Suspicious Login",
        ],
    )

    rules = {
        "Phishing": [
            "Do not open suspicious links or attachments.",
            "Verify the sender through a trusted channel.",
            "Block and report the suspicious sender.",
            "Reset credentials if they may have been exposed.",
        ],
        "Malware": [
            "Isolate the affected endpoint.",
            "Run an approved endpoint security scan.",
            "Preserve logs and suspicious files for investigation.",
            "Restore from a verified clean backup if necessary.",
        ],
        "Ransomware": [
            "Isolate affected systems immediately.",
            "Preserve forensic evidence.",
            "Notify the incident response team.",
            "Restore only from verified clean backups.",
        ],
        "Brute Force": [
            "Block abusive source addresses where appropriate.",
            "Enforce multi-factor authentication.",
            "Apply rate limiting and account lockout policies.",
            "Review authentication logs.",
        ],
        "DDoS": [
            "Activate the organisation's DDoS response plan.",
            "Use approved upstream traffic mitigation.",
            "Monitor service availability.",
            "Contact the hosting or network provider.",
        ],
        "SQL Injection": [
            "Use parameterised database queries.",
            "Validate and safely handle user input.",
            "Review application and database logs.",
            "Patch the affected application.",
        ],
        "Suspicious Login": [
            "Verify the login with the account owner.",
            "Review device and location information.",
            "Revoke suspicious sessions.",
            "Enable multi-factor authentication.",
        ],
    }

    if st.button("Generate Expert Recommendation"):
        st.subheader("Recommended Defensive Actions")

        for item in rules[threat]:
            st.markdown(f"- {item}")

        st.info(
            "Recommendations are based on predefined demonstration rules."
        )


# ==========================================================
# AI PREDICTION
# ==========================================================

def ai_prediction_page():
    hero(
        "AI Threat Prediction",
        "Illustrative risk prediction interface for cybersecurity events.",
    )

    col1, col2 = st.columns(2)

    with col1:
        logins = st.number_input(
            "Failed login attempts",
            min_value=0,
            max_value=500,
            value=10,
        )
        traffic = st.slider("Traffic anomaly score", 0, 100, 30)

    with col2:
        file_alert = st.selectbox("Malicious file alert", ["No", "Yes"])
        port_scan = st.selectbox("Port scanning detected", ["No", "Yes"])

    if st.button("Predict Threat Risk", use_container_width=True):
        score = min(
            100,
            logins * 0.12
            + traffic * 0.45
            + (25 if file_alert == "Yes" else 0)
            + (15 if port_scan == "Yes" else 0),
        )

        st.metric("Illustrative Risk Score", f"{score:.1f}%")
        st.progress(int(score))

        if score >= 75:
            st.error("Prediction category: High risk")
        elif score >= 40:
            st.warning("Prediction category: Moderate risk")
        else:
            st.success("Prediction category: Low risk")

    st.warning(
        "This page uses a demonstration formula, not a trained machine-learning model."
    )


# ==========================================================
# SYSTEM WORKFLOW
# ==========================================================

def workflow_page():
    hero(
        "System Workflow",
        "How CyberGuard AI processes a cybersecurity event.",
    )

    steps = [
        ("01", "Data Input", "Security event or suspicious activity is entered."),
        ("02", "Preprocessing", "Input indicators are organised for analysis."),
        ("03", "Threat Analysis", "Threat characteristics and risk indicators are evaluated."),
        ("04", "Expert System", "Predefined rules generate defensive recommendations."),
        ("05", "AI Assistance", "The assistant explains findings and security actions."),
        ("06", "Reporting", "Results are displayed for review and documentation."),
    ]

    for number, title, description in steps:
        st.markdown(
            f"""
            <div class="panel">
                <h3>{number} · {title}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# REPORTS
# ==========================================================

def reports_page():
    hero(
        "Security Reports",
        "Review and export the demonstration threat-event dataset.",
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Events", len(df))
    c2.metric(
        "Critical Events",
        int((df["Severity"] == "Critical").sum()),
    )
    c3.metric(
        "Blocked Events",
        int((df["Status"] == "Blocked").sum()),
    )

    st.subheader("Threat Event Report")

    st.dataframe(
        df.sort_values("Timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download CSV Report",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="cyberguard_threat_report.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ==========================================================
# AI ASSISTANT
# ==========================================================

def ai_assistant_page():
    hero(
        "CyberGuard AI Assistant",
        "Ask questions about cyber threats, incident response and security.",
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask CyberGuard AI a question...")

    if prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CyberGuard AI is thinking..."):
                answer = ask_groq(
                    prompt,
                    st.session_state.chat_history[:-1],
                )
            st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
        })

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


# ==========================================================
# VOICE ASSISTANT
# ==========================================================

def voice_assistant_page():
    hero(
        "CyberGuard Voice Assistant",
        "Record your question, receive an AI response, and generate audio.",
    )

    if client is None:
        st.error(
            "GROQ_API_KEY is missing. Add it in Streamlit Cloud Secrets."
        )
        return

    if "voice_question" not in st.session_state:
        st.session_state.voice_question = ""

    if "voice_answer" not in st.session_state:
        st.session_state.voice_answer = ""

    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []

    st.subheader("Step 1 — Record your question")

    audio_file = st.audio_input(
        "Record your question",
        sample_rate=16000,
        key="cyberguard_audio_input",
    )

    if st.button("Recognise Voice and Ask AI", use_container_width=True):
        if audio_file is None:
            st.warning("Please record your question first.")
        else:
            try:
                with st.spinner("Converting speech to text..."):
                    transcript = client.audio.transcriptions.create(
                        model=STT_MODEL,
                        file=(
                            "cyberguard_recording.wav",
                            audio_file.getvalue(),
                            "audio/wav",
                        ),
                        response_format="json",
                    )

                question = transcript.text.strip()

                if not question:
                    st.warning("No speech was detected. Please try again.")
                else:
                    st.session_state.voice_question = question

                    with st.spinner("CyberGuard AI is preparing a response..."):
                        answer = ask_groq(
                            question,
                            st.session_state.voice_history,
                        )

                    st.session_state.voice_answer = answer

                    st.session_state.voice_history.extend([
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ])

                    st.session_state.generated_voice_audio = None

            except Exception as exc:
                st.error(f"Voice recognition error: {str(exc)}")

    if st.session_state.voice_question:
        st.subheader("Step 2 — Recognised Question")
        st.info(st.session_state.voice_question)

    if st.session_state.voice_answer:
        st.subheader("Step 3 — AI Response")
        st.markdown(st.session_state.voice_answer)

        st.subheader("Step 4 — Generate Audio")

        if st.button("Generate Audio Response", use_container_width=True):
            try:
                with st.spinner("Generating audio..."):
                    audio_bytes = generate_audio(
                        st.session_state.voice_answer
                    )

                st.session_state.generated_voice_audio = audio_bytes
                st.success("Audio generated successfully.")

            except Exception as exc:
                st.error(
                    "Audio generation error: "
                    f"{str(exc)}"
                )

        if st.session_state.get("generated_voice_audio"):
            st.audio(
                st.session_state.generated_voice_audio,
                format="audio/mp3",
            )

            st.download_button(
                "Download Audio",
                data=st.session_state.generated_voice_audio,
                file_name="cyberguard_response.mp3",
                mime="audio/mpeg",
            )

    if st.button("Clear Voice Conversation"):
        st.session_state.voice_question = ""
        st.session_state.voice_answer = ""
        st.session_state.voice_history = []
        st.session_state.generated_voice_audio = None
        st.rerun()

    st.caption(
        "The microphone starts recording only after you use the recording control. "
        "The browser does not continuously listen in the background."
    )


# ==========================================================
# SIDEBAR AND NAVIGATION
# ==========================================================

st.sidebar.markdown(
    """
    <div style="text-align:center; padding:12px 0 20px;">
        <div style="font-size:42px;">🛡️</div>
        <h2 style="color:white; margin:0;">CYBERGUARD AI</h2>
        <p style="color:#91accb; font-size:11px;">
            INTELLIGENT THREAT ANALYSIS
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<p class="status-online">● System Online</p>',
    unsafe_allow_html=True,
)
st.sidebar.caption("AI-assisted cybersecurity demonstration platform")

pages = [
    st.Page(dashboard_page, title="Dashboard", icon="🏠", default=True),
    st.Page(threat_analysis_page, title="Threat Analysis", icon="🔍"),
    st.Page(threat_intelligence_page, title="Threat Intelligence", icon="🌐"),
    st.Page(expert_system_page, title="Expert System", icon="🧠"),
    st.Page(ai_prediction_page, title="AI Prediction", icon="📈"),
    st.Page(workflow_page, title="System Workflow", icon="⚙️"),
    st.Page(reports_page, title="Reports", icon="📊"),
    st.Page(ai_assistant_page, title="AI Assistant", icon="💬"),
    st.Page(voice_assistant_page, title="Voice Assistant", icon="🎙️"),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()

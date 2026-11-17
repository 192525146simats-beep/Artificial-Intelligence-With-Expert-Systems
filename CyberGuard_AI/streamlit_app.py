
import asyncio
import io
import os
import random
from datetime import datetime, timedelta

import edge_tts
import pandas as pd
import plotly.express as px
import streamlit as st
from groq import Groq


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CyberGuard AI | Intelligent Cyber Threat Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CHAT_MODEL = "openai/gpt-oss-120b"
STT_MODEL = "whisper-large-v3-turbo"
TTS_VOICE = "en-US-JennyNeural"


# ============================================================
# 2. PROFESSIONAL UI DESIGN
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 5%, #132b50 0%, transparent 28%),
        linear-gradient(135deg, #07111f 0%, #0b1729 55%, #101d32 100%);
    color: #edf4ff;
}

header[data-testid="stHeader"] {
    background: rgba(7, 17, 31, 0.85);
}

section[data-testid="stSidebar"] {
    background: #0b1627;
    min-width: 270px !important;
    max-width: 290px !important;
    width: 290px !important;
    border-right: 1px solid #203651;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

section[data-testid="stSidebar"] > div {
    width: 100%;
    overflow-x: hidden;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 1rem;
}

.stMarkdown, p, label {
    color: #dce8f7;
}

h1, h2, h3 {
    color: #f3f7ff !important;
    font-weight: 800 !important;
}

.hero {
    padding: 30px;
    border-radius: 22px;
    background: linear-gradient(120deg, #112d50, #173d68, #10243f);
    border: 1px solid #31557b;
    box-shadow: 0 12px 35px rgba(0,0,0,.25);
    margin-bottom: 22px;
    animation: appear 0.8s ease;
}

.hero h1 {
    font-size: 34px;
    margin-bottom: 8px;
}

.hero p {
    color: #c3d8f2;
    font-size: 15px;
}

@keyframes appear {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.metric-card {
    background: linear-gradient(145deg, #142b47, #102139);
    border: 1px solid #294563;
    border-radius: 17px;
    padding: 20px;
    min-height: 115px;
    box-shadow: 0 8px 25px rgba(0,0,0,.18);
    transition: transform .2s ease, border .2s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: #42a5ff;
}

.metric-label {
    color: #9db6d4;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #ffffff;
    font-size: 29px;
    font-weight: 800;
    margin-top: 8px;
}

.panel {
    background: #102139;
    border: 1px solid #294563;
    border-radius: 17px;
    padding: 20px;
    margin-bottom: 16px;
}

.status-online {
    color: #6ee7b7;
    font-weight: 700;
}

.small-muted {
    color: #9db6d4;
    font-size: 12px;
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
    background: linear-gradient(90deg, #247fc9, #319be8);
}

[data-testid="stDataFrame"] {
    border: 1px solid #294563;
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stMetric"] {
    background: #142b47;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid #294563;
}

.stChatMessage {
    background: #12263f;
    border: 1px solid #294563;
    border-radius: 14px;
}

footer {
    visibility: hidden;
}

@media (max-width: 800px) {
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


# ============================================================
# 3. API CONFIGURATION
# ============================================================

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


def api_status():
    return get_groq_client() is not None


# ============================================================
# 4. DEMONSTRATION DATA
# ============================================================

@st.cache_data
def create_demo_data():
    random.seed(42)

    threat_types = [
        "Malware", "Phishing", "Brute Force",
        "DDoS", "SQL Injection", "Suspicious Login",
        "Ransomware", "Port Scanning"
    ]

    severities = ["Critical", "High", "Medium", "Low"]
    statuses = ["Blocked", "Investigating", "Resolved", "Monitoring"]

    records = []

    for i in range(120):
        risk = round(random.uniform(5, 99), 1)
        severity = (
            "Critical" if risk >= 85 else
            "High" if risk >= 65 else
            "Medium" if risk >= 35 else
            "Low"
        )

        records.append({
            "Event ID": f"CG-{1000 + i}",
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


# ============================================================
# 5. COMMON COMPONENTS
# ============================================================

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


def page_heading(title, description):
    st.markdown(f"## {title}")
    st.caption(description)


# ============================================================
# 6. AI CHAT FUNCTION
# ============================================================

SYSTEM_PROMPT = """
You are CyberGuard AI, an intelligent cybersecurity analysis assistant.

Your responsibilities:
- Explain cybersecurity threats.
- Analyse suspicious activity descriptions.
- Explain malware, phishing, ransomware, DDoS and SQL injection.
- Suggest defensive security measures.
- Help security teams understand risk levels.
- Recommend incident response steps.

Always provide defensive and ethical cybersecurity guidance.
Use clear headings and practical steps.
Do not claim that you have scanned a real network or verified live threats.
"""


def ask_groq(question, history=None):
    client = get_groq_client()

    if client is None:
        return (
            "GROQ_API_KEY is missing. Add your Groq API key "
            "to Streamlit Cloud Secrets."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for item in history[-8:]:
            if item.get("role") in ("user", "assistant"):
                messages.append({
                    "role": item["role"],
                    "content": item["content"]
                })

    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_completion_tokens=1400,
        )
        return response.choices[0].message.content or "No response received."

    except Exception as exc:
        return f"AI chat error: {str(exc)}"


# ============================================================
# 7. VOICE GENERATION USING EDGE TTS
# ============================================================

async def generate_audio_async(text):
    communicator = edge_tts.Communicate(
        text=text,
        voice=TTS_VOICE,
        rate="+0%",
        volume="+0%",
    )

    audio_data = bytearray()

    async for chunk in communicator.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])

    if not audio_data:
        raise RuntimeError("The audio service returned no audio data.")

    return bytes(audio_data)


def generate_audio(text):
    # Keep the spoken response within a manageable size.
    text = text.strip()

    if len(text) > 3500:
        text = text[:3500]
        text += ". The remaining response is available above as text."

    return asyncio.run(generate_audio_async(text))


# ============================================================
# 8. DASHBOARD PAGE
# ============================================================

def dashboard_page():
    hero(
        "CyberGuard AI",
        "Intelligent Cyber Threat Analysis Expert System"
    )

    total = len(df)
    critical = int((df["Severity"] == "Critical").sum())
    high = int((df["Severity"] == "High").sum())
    blocked = int((df["Status"] == "Blocked").sum())
    avg_risk = round(df["Risk Score"].mean(), 1)

    cols = st.columns(5)

    values = [
        ("Total Events", total),
        ("Critical Threats", critical),
        ("High Threats", high),
        ("Blocked Events", blocked),
        ("Average Risk", f"{avg_risk}%"),
    ]

    for col, (label, value) in zip(cols, values):
        with col:
            metric_card(label, value)

    st.write("")

    left, right = st.columns(2)

    with left:
        st.markdown("### Threat Distribution")
        threat_counts = df["Threat Type"].value_counts().reset_index()
        threat_counts.columns = ["Threat Type", "Count"]

        fig = px.pie(
            threat_counts,
            names="Threat Type",
            values="Count",
            hole=0.55,
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### Severity Overview")
        severity_counts = (
            df["Severity"].value_counts()
            .reindex(["Critical", "High", "Medium", "Low"], fill_value=0)
            .reset_index()
        )
        severity_counts.columns = ["Severity", "Count"]

        fig = px.bar(
            severity_counts,
            x="Severity",
            y="Count",
            color="Severity",
            template="plotly_dark",
            text="Count",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recent Threat Events")
    st.dataframe(
        df.sort_values("Timestamp", ascending=False).head(12),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Demonstration dataset: these events are generated sample records, "
        "not verified live network activity."
    )


# ============================================================
# 9. THREAT ANALYSIS PAGE
# ============================================================

def threat_analysis_page():
    hero(
        "Threat Analysis",
        "Evaluate suspicious activity and calculate an illustrative risk score."
    )

    st.markdown("### Enter Activity Details")

    with st.form("threat_analysis_form"):
        activity = st.text_area(
            "Describe the suspicious activity",
            placeholder="Example: Multiple failed login attempts from an unknown IP.",
        )

        failed_logins = st.slider(
            "Number of failed login attempts", 0, 100, 5
        )

        unusual_traffic = st.selectbox(
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
            + {"Normal": 5, "Unusual": 25, "Very High": 40}[unusual_traffic]
            + (25 if suspicious_file == "Yes" else 0)
            + (25 if external_access == "Yes" else 0),
        )

        level = (
            "CRITICAL" if score >= 80 else
            "HIGH" if score >= 60 else
            "MEDIUM" if score >= 30 else
            "LOW"
        )

        st.markdown("### Analysis Result")
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
            st.markdown("**Activity submitted:**")
            st.write(activity)

        st.caption(
            "This is a rule-based demonstration score, not a validated "
            "security detection engine."
        )


# ============================================================
# 10. THREAT INTELLIGENCE PAGE
# ============================================================

def threat_intelligence_page():
    hero(
        "Threat Intelligence",
        "Explore sample threat indicators and event classifications."
    )

    search = st.text_input(
        "Search by IP address, threat type, severity or status"
    )

    filtered = df.copy()

    if search:
        mask = filtered.astype(str).apply(
            lambda col: col.str.contains(search, case=False, na=False)
        ).any(axis=1)
        filtered = filtered[mask]

    st.write(f"**Records found:** {len(filtered)}")

    st.dataframe(
        filtered.sort_values("Risk Score", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "The indicators shown here are synthetic demonstration records. "
        "They are not checked against an external threat-intelligence feed."
    )


# ============================================================
# 11. EXPERT SYSTEM PAGE
# ============================================================

def expert_system_page():
    hero(
        "Cybersecurity Expert System",
        "Rule-based threat interpretation and defensive recommendations."
    )

    threat = st.selectbox(
        "Select the detected threat",
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
            "Block the malicious sender and report the message.",
            "Reset credentials if they may have been exposed.",
        ],
        "Malware": [
            "Isolate the affected endpoint from the network.",
            "Run an approved endpoint security scan.",
            "Preserve logs and suspicious files for investigation.",
            "Restore from a verified clean backup if necessary.",
        ],
        "Ransomware": [
            "Immediately isolate affected systems.",
            "Do not delete forensic evidence.",
            "Notify the incident response team.",
            "Restore only from verified clean backups.",
        ],
        "Brute Force": [
            "Temporarily block abusive source addresses.",
            "Enforce multi-factor authentication.",
            "Apply rate limiting and account lockout policies.",
            "Review authentication logs for compromised accounts.",
        ],
        "DDoS": [
            "Activate the organisation's DDoS response plan.",
            "Use approved upstream filtering or mitigation.",
            "Monitor traffic patterns and service availability.",
            "Contact the hosting or network provider.",
        ],
        "SQL Injection": [
            "Use parameterised database queries.",
            "Validate and safely handle user input.",
            "Review application and database logs.",
            "Test and patch the affected application.",
        ],
        "Suspicious Login": [
            "Verify the login with the account owner.",
            "Review location, device and time information.",
            "Revoke suspicious sessions.",
            "Enable multi-factor authentication.",
        ],
    }

    if st.button("Generate Expert Recommendation"):
        st.markdown("### Recommended Defensive Actions")
        for item in rules[threat]:
            st.markdown(f"- {item}")

        st.info(
            "Recommendations are generated from predefined demonstration "
            "rules. Confirm actions using your organisation's security policy."
        )


# ============================================================
# 12. AI PREDICTION PAGE
# ============================================================

def ai_prediction_page():
    hero(
        "AI Threat Prediction",
        "Illustrative risk prediction interface for cybersecurity events."
    )

    st.markdown("### Enter Threat Indicators")

    col1, col2 = st.columns(2)

    with col1:
        login_count = st.number_input(
            "Failed login attempts", min_value=0, max_value=500, value=10
        )
        traffic = st.slider(
            "Traffic anomaly score", 0, 100, 30
        )

    with col2:
        file_alert = st.selectbox(
            "Malicious file alert", ["No", "Yes"]
        )
        port_scan = st.selectbox(
            "Port scanning detected", ["No", "Yes"]
        )

    if st.button("Predict Threat Risk", use_container_width=True):
        score = min(
            100,
            login_count * 0.12
            + traffic * 0.45
            + (25 if file_alert == "Yes" else 0)
            + (15 if port_scan == "Yes" else 0),
        )

        st.markdown("### Prediction Result")
        st.metric("Illustrative Risk Score", f"{score:.1f}%")
        st.progress(int(score))

        if score >= 75:
            st.error("Prediction category: High risk")
        elif score >= 40:
            st.warning("Prediction category: Moderate risk")
        else:
            st.success("Prediction category: Low risk")

    st.warning(
        "This page uses a demonstration formula, not a trained machine-learning "
        "model. Do not use this score for real-world security decisions."
    )


# ============================================================
# 13. SYSTEM WORKFLOW PAGE
# ============================================================

def workflow_page():
    hero(
        "System Workflow",
        "How the CyberGuard AI demonstration system processes a threat."
    )

    steps = [
        ("01", "Data Input", "Security event or suspicious activity is entered."),
        ("02", "Preprocessing", "Input indicators are organised for analysis."),
        ("03", "Threat Analysis", "Threat characteristics and risk indicators are evaluated."),
        ("04", "Expert System", "Predefined cybersecurity rules generate recommendations."),
        ("05", "AI Assistance", "The AI assistant explains findings and defensive actions."),
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


# ============================================================
# 14. REPORTS PAGE
# ============================================================

def reports_page():
    hero(
        "Security Reports",
        "Review and export the current demonstration threat-event dataset."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Events", len(df))
    col2.metric(
        "Critical Events",
        int((df["Severity"] == "Critical").sum()),
    )
    col3.metric(
        "Blocked Events",
        int((df["Status"] == "Blocked").sum()),
    )

    st.markdown("### Threat Event Report")

    st.dataframe(
        df.sort_values("Timestamp", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV Report",
        data=csv_data,
        file_name="cyberguard_threat_report.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# 15. AI ASSISTANT PAGE
# ============================================================

def ai_assistant_page():
    hero(
        "CyberGuard AI Assistant",
        "Ask questions about cyber threats, incident response and security."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask CyberGuard AI a cybersecurity question..."
    )

    if prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("CyberGuard AI is analysing your question..."):
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


# ============================================================
# 16. VOICE ASSISTANT PAGE
# ============================================================

def voice_assistant_page():
    hero(
        "CyberGuard Voice Assistant",
        "Speak your question, receive an AI response, and generate audio."
    )

    client = get_groq_client()

    if client is None:
        st.error(
            "GROQ_API_KEY is missing. Add it in Streamlit Cloud → "
            "Manage app → Settings → Secrets."
        )
        return

    if "voice_question" not in st.session_state:
        st.session_state.voice_question = ""

    if "voice_answer" not in st.session_state:
        st.session_state.voice_answer = ""

    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []

    st.markdown("### Step 1 — Record your question")

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
                    st.warning("No speech was detected. Please record again.")
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

            except Exception as exc:
                st.error(f"Voice recognition error: {str(exc)}")

    if st.session_state.voice_question:
        st.markdown("### Step 2 — Recognised Question")
        st.info(st.session_state.voice_question)

    if st.session_state.voice_answer:
        st.markdown("### Step 3 — AI Response")
        st.markdown(
            f'<div class="panel">{st.session_state.voice_answer}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Step 4 — Generate Audio")

        if st.button("Generate Audio Response", use_container_width=True):
            try:
                with st.spinner("Generating audio..."):
                    audio_bytes = generate_audio(
                        st.session_state.voice_answer
                    )

                st.session_state.generated_voice_audio = audio_bytes
                st.success("Audio generated successfully.")

            except Exception as exc:
                st.error(f"Audio generation error: {str(exc)}")

        if st.session_state.get("generated_voice_audio"):
            st.audio(
                st.session_state.generated_voice_audio,
                format="audio/mpeg",
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
        "Microphone recording starts only after you interact with the "
        "recording control. This page does not listen continuously in the background."
    )


# ============================================================
# 17. SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown(
    """
    <div style="text-align:center; padding:12px 0 20px;">
        <div style="font-size:42px;">🛡️</div>
        <h2 style="margin:0; color:#ffffff;">CYBERGUARD AI</h2>
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

st.sidebar.caption(
    "AI-assisted cybersecurity demonstration platform"
)

pages = [
    st.Page(
        dashboard_page,
        title="Dashboard",
        icon="🏠",
        default=True,
    ),
    st.Page(
        threat_analysis_page,
        title="Threat Analysis",
        icon="🔍",
    ),
    st.Page(
        threat_intelligence_page,
        title="Threat Intelligence",
        icon="🌐",
    ),
    st.Page(
        expert_system_page,
        title="Expert System",
        icon="🧠",
    ),
    st.Page(
        ai_prediction_page,
        title="AI Prediction",
        icon="📈",
    ),
    st.Page(
        workflow_page,
        title="System Workflow",
        icon="⚙️",
    ),
    st.Page(
        reports_page,
        title="Reports",
        icon="📊",
    ),
    st.Page(
        ai_assistant_page,
        title="AI Assistant",
        icon="💬",
    ),
    st.Page(
        voice_assistant_page,
        title="Voice Assistant",
        icon="🎙️",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()

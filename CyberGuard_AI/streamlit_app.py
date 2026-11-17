import io
import os
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    mic_recorder = None

try:
    from streamlit_float import float_init
    FLOAT_AVAILABLE = True
except ImportError:
    FLOAT_AVAILABLE = False


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CyberGuard AI | Cyber Threat Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_NAME = "CyberGuard AI"
CHAT_MODEL = "openai/gpt-oss-120b"
STT_MODEL = "whisper-large-v3-turbo"
TTS_MODEL = "canopylabs/orpheus-v1-english"

# =========================================================
# GROQ CONFIGURATION
# =========================================================

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

    if Groq is None:
        return None

    return Groq(api_key=key)


# =========================================================
# GLOBAL DESIGN
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080f1d;
    color: #e8eef8;
}

[data-testid="stSidebar"] {
    background: #0d1728;
    border-right: 1px solid #1c2d45;
}

[data-testid="stSidebar"] * {
    color: #e8eef8;
}

.block-container {
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

h1, h2, h3 {
    color: #f3f7ff !important;
}

p, label {
    color: #b7c4d8;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #13243a, #101c2e);
    border: 1px solid #263b56;
    padding: 18px;
    border-radius: 14px;
}

[data-testid="stMetricLabel"] {
    color: #a9bad0 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

[data-testid="stMetricDelta"] {
    font-size: 12px;
}

div.stButton > button {
    border-radius: 9px;
    border: 1px solid #2b6385;
    background: #12334b;
    color: white;
    font-weight: 600;
    min-height: 42px;
}

div.stButton > button:hover {
    background: #18506e;
    border-color: #38bdf8;
    color: white;
}

div[data-testid="stForm"] {
    background: #101e31;
    border: 1px solid #263b56;
    padding: 18px;
    border-radius: 14px;
}

.cyber-header {
    background: linear-gradient(110deg, #10243b, #123b50, #10243b);
    border: 1px solid #24516a;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
}

.cyber-header h1 {
    margin: 0;
    font-size: 30px;
    color: #ffffff;
}

.cyber-header p {
    margin: 8px 0 0 0;
    color: #b9d6e8;
}

.section-card {
    background: #101e31;
    border: 1px solid #263b56;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
}

.small-muted {
    color: #93a8c2;
    font-size: 12px;
}

.status-pill {
    display: inline-block;
    background: #153c35;
    color: #7ee7bd;
    border: 1px solid #286b5b;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 700;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SAMPLE SECURITY DATA
# Clearly marked as demonstration data.
# =========================================================

@st.cache_data
def create_demo_data():
    random.seed(42)

    categories = [
        "Malware", "Phishing", "Brute Force",
        "DDoS", "Port Scanning", "Suspicious Login"
    ]

    severities = ["Critical", "High", "Medium", "Low"]

    sources = [
        "192.168.1.24",
        "10.0.0.18",
        "172.16.0.22",
        "203.0.113.15",
        "198.51.100.42",
        "192.0.2.81"
    ]

    rows = []

    for i in range(100):
        severity = random.choices(
            severities,
            weights=[8, 22, 42, 28]
        )[0]

        rows.append({
            "Event ID": f"CG-{1000+i}",
            "Time": datetime.now() - timedelta(
                minutes=random.randint(1, 1440)
            ),
            "Source IP": random.choice(sources),
            "Threat Type": random.choice(categories),
            "Severity": severity,
            "Risk Score": random.randint(15, 99),
            "Status": random.choice(
                ["Investigating", "Blocked", "Monitoring", "Resolved"]
            )
        })

    return pd.DataFrame(rows)


events = create_demo_data()


def page_header(title, subtitle):
    st.markdown(f"""
    <div class="cyber-header">
        <h1>🛡️ {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def show_demo_notice():
    st.caption(
        "DEMONSTRATION MODE — displayed security events are illustrative "
        "sample data, not verified live attacks."
    )


# =========================================================
# DASHBOARD
# =========================================================

def dashboard_page():

    page_header(
        "Intelligent Cyber Threat Analysis Expert System",
        "AI-assisted security monitoring, threat classification, "
        "risk assessment and incident analysis."
    )

    show_demo_notice()

    total = len(events)
    critical = len(events[events["Severity"] == "Critical"])
    high = len(events[events["Severity"] == "High"])
    blocked = len(events[events["Status"] == "Blocked"])

    avg_risk = int(events["Risk Score"].mean())

    st.markdown("### Security Operations Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Security Events", total, "Sample records")
    c2.metric("Critical Threats", critical, "Requires review")
    c3.metric("High Threats", high, "Priority monitoring")
    c4.metric("Blocked Events", blocked, "Sample status")
    c5.metric("Average Risk", f"{avg_risk}/100", "Illustrative score")

    st.markdown("### Threat Monitoring Analytics")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Threat Category Distribution")

        category_data = (
            events["Threat Type"]
            .value_counts()
            .reset_index()
        )
        category_data.columns = ["Threat", "Count"]

        fig = px.pie(
            category_data,
            names="Threat",
            values="Count",
            hole=0.55,
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dce8f5",
            legend_title="Threat category",
            margin=dict(t=20, b=20, l=10, r=10)
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### Threat Severity Distribution")

        severity_data = (
            events["Severity"]
            .value_counts()
            .reindex(["Critical", "High", "Medium", "Low"])
            .fillna(0)
            .reset_index()
        )
        severity_data.columns = ["Severity", "Count"]

        fig = px.bar(
            severity_data,
            x="Severity",
            y="Count",
            color="Severity",
            color_discrete_map={
                "Critical": "#ef4444",
                "High": "#f97316",
                "Medium": "#eab308",
                "Low": "#22c55e"
            }
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dce8f5",
            showlegend=False,
            margin=dict(t=20, b=20, l=10, r=10)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Security Event Activity")

    hourly = events.copy()
    hourly["Hour"] = hourly["Time"].dt.floor("h")

    timeline = (
        hourly.groupby("Hour")
        .size()
        .reset_index(name="Events")
        .sort_values("Hour")
    )

    fig = px.area(
        timeline,
        x="Hour",
        y="Events",
        markers=True
    )

    fig.update_traces(
        line_color="#38bdf8",
        fillcolor="rgba(56,189,248,0.15)"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dce8f5",
        xaxis_title="Time",
        yaxis_title="Number of events"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recent Security Events")

    recent = events.sort_values("Time", ascending=False).head(10)

    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div class="section-card">
        <h3>🧠 Expert System Capabilities</h3>
        <p>
        • Threat identification and classification<br>
        • Risk scoring and severity assessment<br>
        • Rule-based expert recommendations<br>
        • AI-assisted security explanations<br>
        • Incident reporting and monitoring
        </p>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# THREAT ANALYSIS
# =========================================================

def threat_analysis_page():

    page_header(
        "Threat Analysis",
        "Analyze suspicious IP addresses, events and security indicators."
    )

    with st.form("threat_form"):
        ip = st.text_input(
            "Source IP address",
            placeholder="Example: 192.168.1.100"
        )

        threat_type = st.selectbox(
            "Observed activity",
            [
                "Suspicious Login",
                "Brute Force",
                "Malware",
                "Phishing",
                "DDoS",
                "Port Scanning",
                "Unknown"
            ]
        )

        failed_logins = st.number_input(
            "Failed login attempts",
            min_value=0,
            max_value=10000,
            value=3
        )

        unusual_traffic = st.selectbox(
            "Network traffic pattern",
            ["Normal", "Unusual", "Extremely High"]
        )

        submitted = st.form_submit_button(
            "Analyze Security Event",
            use_container_width=True
        )

    if submitted:
        score = 15

        score += min(int(failed_logins) * 5, 40)

        if unusual_traffic == "Unusual":
            score += 20
        elif unusual_traffic == "Extremely High":
            score += 35

        if threat_type in ["Malware", "DDoS", "Brute Force"]:
            score += 20

        score = min(score, 100)

        if score >= 75:
            severity = "CRITICAL"
            recommendation = (
                "Escalate for analyst review. Investigate the source, "
                "preserve relevant logs and apply approved containment."
            )
        elif score >= 50:
            severity = "HIGH"
            recommendation = (
                "Investigate the event, review related activity and "
                "consider additional monitoring."
            )
        elif score >= 30:
            severity = "MEDIUM"
            recommendation = (
                "Monitor the source and validate the activity against "
                "known legitimate behavior."
            )
        else:
            severity = "LOW"
            recommendation = (
                "Continue routine monitoring and retain the event record."
            )

        st.markdown("### Analysis Result")

        a, b = st.columns(2)
        a.metric("Illustrative Risk Score", f"{score}/100")
        b.metric("Severity", severity)

        st.progress(score / 100)

        st.info(recommendation)

        st.caption(
            "This is a rule-based demonstration score, not a validated "
            "machine-learning prediction."
        )


# =========================================================
# THREAT INTELLIGENCE
# =========================================================

def threat_intelligence_page():

    page_header(
        "Threat Intelligence",
        "Review threat indicators and security event patterns."
    )

    show_demo_notice()

    selected = st.multiselect(
        "Filter by threat category",
        sorted(events["Threat Type"].unique()),
        default=sorted(events["Threat Type"].unique())
    )

    filtered = events[events["Threat Type"].isin(selected)]

    st.metric("Matching events", len(filtered))

    st.dataframe(
        filtered.sort_values("Risk Score", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Threat Intelligence Guidance")

    st.info(
        "For operational threat intelligence, connect a verified feed "
        "such as an authorized SIEM, MISP instance, or trusted threat "
        "intelligence provider. The current records are sample data."
    )


# =========================================================
# EXPERT SYSTEM
# =========================================================

def expert_system_page():

    page_header(
        "Cybersecurity Expert System",
        "Rule-based reasoning and recommended defensive actions."
    )

    st.markdown("### Enter security conditions")

    login = st.number_input(
        "Failed login attempts",
        min_value=0,
        max_value=1000,
        value=2
    )

    traffic = st.selectbox(
        "Traffic behavior",
        ["Normal", "Abnormal", "Very High"]
    )

    malware = st.selectbox(
        "Malware indicator",
        ["Not detected", "Suspicious file", "Confirmed detection"]
    )

    if st.button("Run Expert System", use_container_width=True):

        findings = []

        if login >= 10:
            findings.append(
                ("High", "Possible brute-force activity",
                 "Review authentication logs and apply account protection.")
            )
        elif login >= 5:
            findings.append(
                ("Medium", "Repeated login failures",
                 "Monitor the account and verify legitimate access.")
            )

        if traffic == "Very High":
            findings.append(
                ("High", "Unusually high network traffic",
                 "Investigate possible DDoS or data transfer activity.")
            )
        elif traffic == "Abnormal":
            findings.append(
                ("Medium", "Abnormal network behavior",
                 "Review network logs and compare with baseline traffic.")
            )

        if malware == "Confirmed detection":
            findings.append(
                ("Critical", "Malware indicator confirmed by input",
                 "Follow your incident response process and isolate "
                 "affected assets where authorized.")
            )
        elif malware == "Suspicious file":
            findings.append(
                ("High", "Suspicious file reported",
                 "Analyze the file in an approved isolated environment.")
            )

        if not findings:
            st.success("No rule was triggered by the supplied conditions.")

        for level, title, action in findings:
            if level == "Critical":
                st.error(f"{level}: {title}")
            elif level == "High":
                st.warning(f"{level}: {title}")
            else:
                st.info(f"{level}: {title}")

            st.write("Recommended action:", action)


# =========================================================
# AI PREDICTION
# =========================================================

def ai_prediction_page():

    page_header(
        "AI Threat Prediction",
        "Estimate a risk level from the supplied security indicators."
    )

    st.warning(
        "The following is an illustrative baseline calculation. "
        "It is not a prediction from your saved trained model."
    )

    col1, col2 = st.columns(2)

    with col1:
        packet_rate = st.slider(
            "Network packet rate",
            0, 10000, 1500
        )

        failed = st.slider(
            "Failed login attempts",
            0, 100, 5
        )

    with col2:
        unusual_ports = st.slider(
            "Unusual port connections",
            0, 100, 2
        )

        traffic_anomaly = st.slider(
            "Traffic anomaly level",
            0, 100, 20
        )

    if st.button("Predict Threat Risk", use_container_width=True):

        score = (
            min(packet_rate / 10000 * 25, 25)
            + min(failed * 1.2, 30)
            + min(unusual_ports * 0.8, 20)
            + traffic_anomaly * 0.25
        )

        score = int(min(score, 100))

        st.markdown("### Prediction Summary")

        st.metric("Illustrative Risk Score", f"{score}/100")
        st.progress(score / 100)

        if score >= 70:
            st.error("HIGH RISK — Requires security analyst review.")
        elif score >= 40:
            st.warning("MEDIUM RISK — Further investigation recommended.")
        else:
            st.success("LOW RISK — Continue routine monitoring.")


# =========================================================
# SYSTEM WORKFLOW
# =========================================================

def workflow_page():

    page_header(
        "System Architecture & Workflow",
        "How the Intelligent Cyber Threat Analysis Expert System works."
    )

    steps = [
        ("01", "Data Collection",
         "Collect authorized security logs and event records."),
        ("02", "Data Preprocessing",
         "Clean, validate and prepare the event information."),
        ("03", "Feature Extraction",
         "Identify useful indicators such as IP, traffic and login patterns."),
        ("04", "Threat Analysis",
         "Apply expert rules and available AI/ML models."),
        ("05", "Risk Classification",
         "Classify findings by severity and risk score."),
        ("06", "Recommendations",
         "Present suggested defensive actions for analyst review."),
        ("07", "Reporting",
         "Display event history, charts and investigation reports.")
    ]

    for number, title, description in steps:
        st.markdown(f"""
        <div class="section-card">
            <span class="status-pill">STEP {number}</span>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# REPORTS
# =========================================================

def reports_page():

    page_header(
        "Security Reports",
        "Review, filter and export security event records."
    )

    show_demo_notice()

    severity = st.multiselect(
        "Select severity",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"]
    )

    report = events[events["Severity"].isin(severity)].copy()

    st.metric("Records in report", len(report))

    st.dataframe(
        report.sort_values("Risk Score", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv_data = report.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Security Report (CSV)",
        data=csv_data,
        file_name="cyberguard_security_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# VOICE ASSISTANT
# =========================================================

SYSTEM_PROMPT = """
You are CyberGuard AI, a cybersecurity assistant for defensive,
authorized security analysis.

Explain cybersecurity concepts clearly. Help users understand alerts,
security logs, threat classifications, risk indicators and defensive
recommendations.

Do not claim that you have scanned a network, blocked an attacker,
verified an IP address or detected a live threat unless connected
evidence is actually provided.
"""


def ask_groq(user_message, history=None):

    client = get_groq_client()

    if client is None:
        raise RuntimeError(
            "Groq is not configured. Add GROQ_API_KEY to Streamlit Secrets."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-10:])

    messages.append({
        "role": "user",
        "content": user_message
    })

    result = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=1200
    )

    return result.choices[0].message.content


def transcribe_audio(audio_bytes):

    client = get_groq_client()

    if client is None:
        raise RuntimeError("Groq API key is not configured.")

    result = client.audio.transcriptions.create(
        file=("cyberguard_audio.wav", audio_bytes),
        model=STT_MODEL,
        response_format="text"
    )

    if isinstance(result, str):
        return result

    return getattr(result, "text", str(result))


def speak_text(text_to_speak):

    client = get_groq_client()

    if client is None:
        raise RuntimeError("Groq API key is not configured.")

    # Orpheus TTS has a 200-character input limit.
    short_text = text_to_speak[:200]

    audio_response = client.audio.speech.create(
        model=TTS_MODEL,
        voice="hannah",
        input=short_text,
        response_format="wav"
    )

    return audio_response.read()


def voice_assistant_page():

    page_header(
        "CyberGuard AI Voice Assistant",
        "Ask cybersecurity questions using text or your microphone."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "voice_reply" not in st.session_state:
        st.session_state.voice_reply = ""

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input(
        "Ask CyberGuard AI a cybersecurity question..."
    )

    if user_message:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            answer = ask_groq(
                user_message,
                st.session_state.chat_history[:-1]
            )

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()

        except Exception as e:
            st.error(f"Groq chat error: {e}")

    st.markdown("### 🎙️ Voice Input")

    if mic_recorder is None:
        st.warning(
            "Microphone package is missing. Add "
            "streamlit-mic-recorder to requirements.txt."
        )
    else:
        audio = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording",
            just_once=True,
            use_container_width=True,
            key="main_voice_recorder"
        )

        if audio and audio.get("bytes"):
            if st.button("Transcribe and Ask CyberGuard AI"):
                try:
                    text = transcribe_audio(audio["bytes"])

                    if text.strip():
                        st.write("Recognized speech:", text)

                        answer = ask_groq(
                            text,
                            st.session_state.chat_history
                        )

                        st.session_state.chat_history.extend([
                            {"role": "user", "content": text},
                            {"role": "assistant", "content": answer}
                        ])

                        st.session_state.voice_reply = answer
                        st.rerun()

                except Exception as e:
                    st.error(f"Voice assistant error: {e}")

    if st.session_state.voice_reply:
        st.markdown("### 🔊 Female Voice Response")

        if st.button("Speak Answer"):
            try:
                audio_bytes = speak_text(
                    st.session_state.voice_reply
                )
                st.audio(audio_bytes, format="audio/wav")

            except Exception as e:
                st.error(f"Text-to-speech error: {e}")

    if st.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.session_state.voice_reply = ""
        st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div style="text-align:center;padding:12px 0 20px 0">
        <div style="font-size:42px">🛡️</div>
        <h2 style="margin:0;color:#ffffff">CyberGuard AI</h2>
        <p class="small-muted">Intelligent Security Platform</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### Navigation")

    st.markdown(
        '<span class="status-pill">SYSTEM DEMO</span>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.caption("Cyber Threat Analysis Expert System")
    st.caption("AI • Expert Rules • Risk Assessment")


# =========================================================
# MULTIPAGE NAVIGATION
# =========================================================

pages = [
    st.Page(
        dashboard_page,
        title="Dashboard",
        icon="🏠",
        default=True
    ),
    st.Page(
        threat_analysis_page,
        title="Threat Analysis",
        icon="🔍"
    ),
    st.Page(
        threat_intelligence_page,
        title="Threat Intelligence",
        icon="🌐"
    ),
    st.Page(
        expert_system_page,
        title="Expert System",
        icon="🧠"
    ),
    st.Page(
        ai_prediction_page,
        title="AI Prediction",
        icon="🤖"
    ),
    st.Page(
        workflow_page,
        title="System Workflow",
        icon="⚙️"
    ),
    st.Page(
        reports_page,
        title="Reports",
        icon="📊"
    ),
    st.Page(
        voice_assistant_page,
        title="Voice Assistant",
        icon="🎙️"
    )
]

selected_page = st.navigation(pages)
selected_page.run()


# =========================================================
# FLOATING VOICE ASSISTANT
# =========================================================

if FLOAT_AVAILABLE and mic_recorder is not None:

    try:
        float_init()

        floating_panel = st.container()

        floating_panel.float(
            "bottom: 1rem; right: 1rem; width: 340px; "
            "z-index: 999; background: #10243b; "
            "border: 1px solid #38bdf8; border-radius: 14px; "
            "padding: 12px;"
        )

        with floating_panel:
            with st.expander("🎙️ CyberGuard Quick Assistant"):

                quick_question = st.text_input(
                    "Ask CyberGuard AI",
                    key="floating_question"
                )

                if st.button(
                    "Send Question",
                    key="floating_send",
                    use_container_width=True
                ):
                    if quick_question.strip():
                        try:
                            reply = ask_groq(quick_question)
                            st.session_state.floating_reply = reply
                        except Exception as e:
                            st.session_state.floating_reply = (
                                f"Assistant error: {e}"
                            )

                if st.session_state.get("floating_reply"):
                    st.write(st.session_state.floating_reply)

    except Exception:
        with st.sidebar:
            st.markdown("### 🎙️ Quick Assistant")
            st.caption(
                "Floating panel is unavailable in this deployment. "
                "Open the Voice Assistant page instead."
            )


import io
import os
import random
import tempfile
import wave
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None


# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="CyberGuard AI | Intelligent Cyber Threat Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CHAT_MODEL = "openai/gpt-oss-120b"
STT_MODEL = "whisper-large-v3-turbo"
TTS_MODEL = "canopylabs/orpheus-v1-english"
FEMALE_VOICE = "hannah"


# =====================================================
# ANIMATED UI AND SIDEBAR FIX
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background:
      radial-gradient(circle at 10% 0%, #12334b 0%, transparent 28%),
      radial-gradient(circle at 90% 10%, #10274b 0%, transparent 30%),
      #07111f;
    color: #edf5ff;
}

[data-testid="stHeader"] {
    background: rgba(7,17,31,.9);
}

[data-testid="stSidebar"] {
    min-width: 290px !important;
    max-width: 290px !important;
    background: linear-gradient(180deg,#0d2036,#091525) !important;
    border-right: 1px solid #294967;
}

[data-testid="stSidebar"] > div {
    width: 290px !important;
}

[data-testid="stSidebarContent"] {
    height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding-bottom: 30px;
}

.block-container {
    max-width: 1600px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

h1,h2,h3,h4 {
    color: #f4f8ff !important;
}

p,label {
    color: #b7c8dc;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 28px;
    margin-bottom: 22px;
    border: 1px solid #27627c;
    border-radius: 18px;
    background: linear-gradient(110deg,#102c49,#12465a,#10243f);
    animation: fadeUp .7s ease both;
    box-shadow: 0 10px 35px rgba(0,0,0,.22);
}

.hero:after {
    content: "";
    position: absolute;
    width: 230px;
    height: 230px;
    right: -70px;
    top: -120px;
    border: 1px solid rgba(103,232,249,.35);
    border-radius: 50%;
    box-shadow: 0 0 0 25px rgba(56,189,248,.04),
                0 0 0 55px rgba(56,189,248,.025);
    animation: orbit 5s ease-in-out infinite;
}

.hero h1 {
    font-size: clamp(25px,3vw,36px);
    margin: 0;
    position: relative;
    z-index: 1;
}

.hero p {
    margin: 9px 0 0;
    position: relative;
    z-index: 1;
}

.eyebrow {
    color: #67e8f9;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 9px;
}

.panel {
    background: linear-gradient(145deg,#132942,#0d1d31);
    border: 1px solid #294662;
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 12px;
    animation: fadeUp .6s ease both;
    transition: transform .2s ease, border-color .2s ease;
}

.panel:hover {
    transform: translateY(-3px);
    border-color: #38bdf8;
}

.metric-card {
    background: linear-gradient(145deg,#17324f,#102239);
    border: 1px solid #31516d;
    border-radius: 14px;
    padding: 17px;
    min-height: 120px;
    animation: fadeUp .6s ease both;
    transition: .2s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(56,189,248,.15);
}

.metric-label {
    color: #b4c9df;
    font-size: 12px;
}

.metric-value {
    color: white;
    font-size: 29px;
    font-weight: 800;
    margin-top: 10px;
}

.metric-note {
    color: #67e8f9;
    font-size: 11px;
    margin-top: 5px;
}

.voice-box {
    background: linear-gradient(145deg,#123b54,#112440);
    border: 1px solid #347b96;
    border-radius: 18px;
    padding: 20px;
    animation: glow 3s infinite alternate;
}

.voice-orb {
    width: 78px;
    height: 78px;
    border-radius: 50%;
    margin: 5px auto 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    background: radial-gradient(circle,#1c7895,#102d4a);
    border: 1px solid #67e8f9;
    box-shadow: 0 0 0 9px rgba(56,189,248,.08);
    animation: float 3s ease-in-out infinite;
}

.tag {
    display: inline-block;
    background: #10394d;
    border: 1px solid #27627c;
    color: #a5f3fc;
    padding: 5px 10px;
    margin: 3px;
    border-radius: 30px;
    font-size: 11px;
}

.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #34d399;
    margin-right: 7px;
    animation: pulse 1.8s infinite;
}

div.stButton > button {
    min-height: 43px;
    border-radius: 10px;
    border: 1px solid #34718e;
    background: linear-gradient(100deg,#12415c,#15536b);
    color: white;
    font-weight: 700;
    transition: .2s ease;
}

div.stButton > button:hover {
    background: #176783;
    border-color: #67e8f9;
    transform: translateY(-2px);
    color: white;
}

[data-testid="stMetric"] {
    background: #12263d;
    border: 1px solid #294662;
    border-radius: 12px;
    padding: 14px;
}

[data-testid="stChatMessage"] {
    background: #12263d;
    border: 1px solid #294662;
    border-radius: 13px;
}

@keyframes fadeUp {
    from {opacity:0;transform:translateY(13px);}
    to {opacity:1;transform:translateY(0);}
}

@keyframes pulse {
    0% {box-shadow:0 0 0 0 rgba(52,211,153,.6);}
    70% {box-shadow:0 0 0 8px rgba(52,211,153,0);}
    100% {box-shadow:0 0 0 0 rgba(52,211,153,0);}
}

@keyframes orbit {
    0%,100% {transform:scale(.94);opacity:.6;}
    50% {transform:scale(1.06);opacity:1;}
}

@keyframes float {
    0%,100% {transform:translateY(0);}
    50% {transform:translateY(-7px);}
}

@keyframes glow {
    from {box-shadow:0 0 10px rgba(56,189,248,.05);}
    to {box-shadow:0 0 25px rgba(56,189,248,.18);}
}

@media(max-width:800px) {
    [data-testid="stSidebar"] {
        min-width:250px !important;
        max-width:250px !important;
    }
    [data-testid="stSidebar"] > div {
        width:250px !important;
    }
}

footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# =====================================================
# GROQ CONNECTION
# =====================================================

def get_api_key():
    try:
        if st.secrets.get("GROQ_API_KEY"):
            return st.secrets["GROQ_API_KEY"]

        if "groq" in st.secrets:
            return st.secrets["groq"]["api_key"]
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


@st.cache_resource
def get_client():
    key = get_api_key()

    if not key or Groq is None:
        return None

    return Groq(api_key=key)


def require_client():
    client = get_client()

    if client is None:
        raise RuntimeError(
            "Groq API key is missing. Add GROQ_API_KEY in Streamlit Secrets."
        )

    return client


# =====================================================
# DEMONSTRATION DATA
# =====================================================

@st.cache_data
def get_events():
    rng = random.Random(42)

    threats = [
        "Malware", "Phishing", "Brute Force", "DDoS",
        "Port Scanning", "Suspicious Login", "Data Exfiltration"
    ]

    severities = ["Critical", "High", "Medium", "Low"]

    statuses = ["Investigating", "Blocked", "Monitoring", "Resolved"]

    ips = [
        "203.0.113.24", "198.51.100.17",
        "192.0.2.48", "10.0.0.18",
        "172.16.0.22", "192.168.1.105"
    ]

    data = []

    for i in range(120):
        data.append({
            "Event ID": f"CG-{2026000+i}",
            "Timestamp": datetime.now() - timedelta(
                minutes=rng.randint(1,10080)
            ),
            "Source IP": rng.choice(ips),
            "Threat Type": rng.choice(threats),
            "Severity": rng.choices(
                severities,
                weights=[7,19,43,31]
            )[0],
            "Risk Score": rng.randint(12,99),
            "Status": rng.choice(statuses)
        })

    return pd.DataFrame(data)


events = get_events()


# =====================================================
# COMMON UI
# =====================================================

def header(title, subtitle):
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">INTELLIGENT SECURITY OPERATIONS CENTER</div>
      <h1>🛡️ {title}</h1>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def demo_notice():
    st.caption(
        "DEMO MODE: These are illustrative sample records, not live network detections."
    )


def metric(label, value, note, icon):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{icon} &nbsp; {label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# DASHBOARD
# =====================================================

def dashboard_page():
    header(
        "Intelligent Cyber Threat Analysis Expert System",
        "Unified AI-assisted cyber threat monitoring, risk assessment, "
        "expert-system reasoning and incident reporting."
    )

    demo_notice()

    total = len(events)
    critical = int((events["Severity"] == "Critical").sum())
    high = int((events["Severity"] == "High").sum())
    blocked = int((events["Status"] == "Blocked").sum())
    risk = int(events["Risk Score"].mean())

    st.markdown("### Security Operations Overview")

    cols = st.columns(5)

    cards = [
        ("Security Events", total, "Sample records", "📡"),
        ("Critical Threats", critical, "Priority review", "🚨"),
        ("High Threats", high, "Elevated risk", "⚠️"),
        ("Blocked Events", blocked, "Sample status", "🛡️"),
        ("Average Risk", f"{risk}/100", "Illustrative score", "📈")
    ]

    for col, item in zip(cols, cards):
        with col:
            metric(*item)

    left, right = st.columns(2)

    with left:
        st.markdown("### Threat Category Distribution")

        category = events["Threat Type"].value_counts().reset_index()
        category.columns = ["Threat", "Count"]

        fig = px.pie(
            category,
            names="Threat",
            values="Count",
            hole=.55
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### Threat Severity")

        severity = (
            events["Severity"].value_counts()
            .reindex(["Critical","High","Medium","Low"])
            .fillna(0)
            .rename_axis("Severity")
            .reset_index(name="Count")
        )

        fig = px.bar(
            severity,
            x="Severity",
            y="Count",
            color="Severity",
            color_discrete_map={
                "Critical":"#ef4444",
                "High":"#f97316",
                "Medium":"#eab308",
                "Low":"#22c55e"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Security Event Timeline")

    timeline_data = events.copy()
    timeline_data["Hour"] = timeline_data["Timestamp"].dt.floor("h")

    timeline = (
        timeline_data.groupby("Hour")
        .size()
        .reset_index(name="Events")
    )

    fig = px.area(
        timeline,
        x="Hour",
        y="Events",
        markers=True
    )

    fig.update_traces(
        line_color="#38bdf8",
        fillcolor="rgba(56,189,248,.16)"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recent Security Events")

    st.dataframe(
        events.sort_values("Timestamp",ascending=False).head(12),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div class="panel">
      <h3>🧠 Intelligent System Capabilities</h3>
      <span class="tag">Threat Classification</span>
      <span class="tag">Risk Assessment</span>
      <span class="tag">Expert Rules</span>
      <span class="tag">AI Assistant</span>
      <span class="tag">Security Reports</span>
      <p>Centralized analysis of security indicators, risk levels,
      expert recommendations and incident history.</p>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# THREAT ANALYSIS
# =====================================================

def threat_analysis_page():
    header("Threat Analysis","Analyze suspicious events and security indicators.")

    with st.form("analysis_form"):
        c1,c2 = st.columns(2)

        with c1:
            ip = st.text_input("Source IP address")
            kind = st.selectbox(
                "Threat category",
                ["Suspicious Login","Brute Force","Malware",
                 "Phishing","DDoS","Port Scanning","Unknown"]
            )

        with c2:
            failures = st.number_input(
                "Failed login attempts",0,10000,2
            )
            traffic = st.selectbox(
                "Traffic pattern",
                ["Normal","Unusual","Extremely High"]
            )

        submit = st.form_submit_button(
            "🔍 Analyze Event",
            use_container_width=True
        )

    if submit:
        score = 15 + min(failures*5,40)

        if traffic == "Unusual":
            score += 20
        elif traffic == "Extremely High":
            score += 35

        if kind in ["Malware","DDoS","Brute Force"]:
            score += 20

        score = min(score,100)

        level = (
            "CRITICAL" if score>=75 else
            "HIGH" if score>=50 else
            "MEDIUM" if score>=30 else "LOW"
        )

        a,b = st.columns(2)
        a.metric("Risk Score",f"{score}/100")
        b.metric("Severity",level)

        st.progress(score/100)

        st.info(f"Source: {ip or 'Not supplied'} | Activity: {kind}")

        recommendations = {
            "CRITICAL":"Escalate for analyst review and follow approved containment procedures.",
            "HIGH":"Investigate related events and review authentication and network logs.",
            "MEDIUM":"Validate the event against normal behavior and monitor.",
            "LOW":"Retain the record and continue routine monitoring."
        }

        st.warning(recommendations[level])

        st.caption("This is a demonstration rule-based score, not a trained model prediction.")


# =====================================================
# THREAT INTELLIGENCE
# =====================================================

def threat_intelligence_page():
    header("Threat Intelligence","Review event indicators and threat patterns.")
    demo_notice()

    categories = sorted(events["Threat Type"].unique())

    selected = st.multiselect(
        "Threat category",
        categories,
        default=categories
    )

    filtered = events[events["Threat Type"].isin(selected)]

    a,b,c = st.columns(3)
    a.metric("Matching events",len(filtered))
    b.metric("Unique IP addresses",filtered["Source IP"].nunique())
    c.metric("Average risk",f"{filtered['Risk Score'].mean():.1f}")

    st.dataframe(
        filtered.sort_values("Risk Score",ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Connect an authorized SIEM or verified threat intelligence feed "
        "to use real operational indicators."
    )


# =====================================================
# EXPERT SYSTEM
# =====================================================

def expert_system_page():
    header("Cybersecurity Expert System","Rule-based reasoning and defensive recommendations.")

    a,b = st.columns(2)

    with a:
        failed = st.number_input("Failed login attempts",0,1000,2)
        traffic = st.selectbox(
            "Traffic behaviour",["Normal","Abnormal","Very High"]
        )

    with b:
        malware = st.selectbox(
            "Malware indicator",
            ["Not detected","Suspicious file","Confirmed detection"]
        )
        privilege = st.selectbox(
            "Unexpected privilege change",["No","Yes"]
        )

    if st.button("🧠 Run Expert System",use_container_width=True):
        findings = []

        if failed>=10:
            findings.append(("HIGH","Possible brute-force activity",
                "Review authentication logs and investigate the source."))
        elif failed>=5:
            findings.append(("MEDIUM","Repeated login failures",
                "Monitor the account and verify legitimate access."))

        if traffic=="Very High":
            findings.append(("HIGH","Unusually high network traffic",
                "Investigate traffic volume and destination patterns."))
        elif traffic=="Abnormal":
            findings.append(("MEDIUM","Abnormal network behaviour",
                "Compare activity with normal traffic baselines."))

        if malware=="Confirmed detection":
            findings.append(("CRITICAL","Malware indicator reported",
                "Follow your incident response procedure."))
        elif malware=="Suspicious file":
            findings.append(("HIGH","Suspicious file reported",
                "Analyze the file in an approved isolated environment."))

        if privilege=="Yes":
            findings.append(("HIGH","Unexpected privilege change",
                "Audit privileged accounts and verify the change."))

        if not findings:
            st.success("No rule was triggered.")

        for level,title,advice in findings:
            if level=="CRITICAL":
                st.error(f"🚨 {level}: {title}")
            elif level=="HIGH":
                st.warning(f"⚠️ {level}: {title}")
            else:
                st.info(f"ℹ️ {level}: {title}")

            st.write("Recommended action:",advice)


# =====================================================
# AI PREDICTION
# =====================================================

def ai_prediction_page():
    header("AI Threat Prediction","Estimate risk using network indicators.")

    st.warning(
        "This page currently uses a demonstration formula, not your saved "
        "trained machine-learning model."
    )

    a,b = st.columns(2)

    with a:
        packets = st.slider("Network packet rate",0,10000,1500)
        failures = st.slider("Failed login attempts",0,100,5)

    with b:
        ports = st.slider("Unusual port connections",0,100,2)
        anomaly = st.slider("Traffic anomaly level",0,100,20)

    if st.button("🤖 Predict Risk",use_container_width=True):
        score = int(min(
            min(packets/10000*25,25)
            + min(failures*1.2,30)
            + min(ports*.8,20)
            + anomaly*.25,
            100
        ))

        st.metric("Illustrative Risk Score",f"{score}/100")
        st.progress(score/100)

        if score>=70:
            st.error("HIGH RISK — Analyst review required.")
        elif score>=40:
            st.warning("MEDIUM RISK — Further investigation recommended.")
        else:
            st.success("LOW RISK — Continue routine monitoring.")


# =====================================================
# SYSTEM WORKFLOW
# =====================================================

def workflow_page():
    header("System Architecture & Workflow","Processing pipeline of CyberGuard AI.")

    stages = [
        ("01","Data Collection","Collect authorized security logs and events."),
        ("02","Data Preprocessing","Clean and validate input records."),
        ("03","Feature Extraction","Identify IPs, ports and traffic indicators."),
        ("04","Threat Analysis","Apply expert rules and AI/ML models."),
        ("05","Risk Classification","Classify severity and risk scores."),
        ("06","Recommendations","Provide explainable defensive actions."),
        ("07","Reporting","Generate incident history and reports.")
    ]

    for number,title,description in stages:
        st.markdown(f"""
        <div class="panel">
          <span class="tag">STEP {number}</span>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
        """,unsafe_allow_html=True)


# =====================================================
# REPORTS
# =====================================================

def reports_page():
    header("Security Reports","Filter and export security event records.")
    demo_notice()

    levels = st.multiselect(
        "Severity",
        ["Critical","High","Medium","Low"],
        default=["Critical","High","Medium","Low"]
    )

    report = events[events["Severity"].isin(levels)]

    st.metric("Report records",len(report))

    st.dataframe(
        report,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download CSV Report",
        data=report.to_csv(index=False).encode("utf-8"),
        file_name="cyberguard_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# =====================================================
# AI CHAT
# =====================================================

SYSTEM_PROMPT = """
You are CyberGuard AI, a professional cybersecurity assistant.

Help users understand:
- Network security
- Malware and phishing
- Threat intelligence
- Security logs
- Incident response
- Risk assessment
- Defensive cybersecurity practices

Give clear, structured and practical answers.

Never claim that you scanned a network, blocked an attacker or detected
a live threat unless verified evidence from a connected system is supplied.
"""


def ask_groq(question,history):
    client = require_client()

    messages = [{"role":"system","content":SYSTEM_PROMPT}]
    messages.extend(history[-12:])
    messages.append({"role":"user","content":question})

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=.45,
        max_completion_tokens=1400
    )

    return response.choices[0].message.content or "No response generated."


# =====================================================
# VOICE RECOGNITION
# =====================================================

def recognize_voice(audio_file):
    client = require_client()

    audio_bytes = audio_file.getvalue()

    if not audio_bytes:
        raise ValueError("Recording is empty. Please record again.")

    result = client.audio.transcriptions.create(
        model=STT_MODEL,
        file=("cyberguard.wav",audio_bytes,"audio/wav"),
        response_format="json",
        language="en"
    )

    transcript = getattr(result,"text","")

    if not transcript.strip():
        raise ValueError(
            "No speech recognized. Please speak clearly and record again."
        )

    return transcript.strip()


# =====================================================
# FEMALE VOICE GENERATION
# =====================================================

def split_text(text,limit=185):
    text = " ".join(text.replace("\n"," ").split())
    chunks = []

    while text:
        if len(text)<=limit:
            chunks.append(text)
            break

        position = text.rfind(" ",0,limit)

        if position<80:
            position = limit

        chunks.append(text[:position].strip())
        text = text[position:].strip()

    return chunks


def create_female_voice(text):
    client = require_client()

    chunks = split_text(text,185)

    if not chunks:
        raise ValueError("No text to speak.")

    original_count = len(chunks)
    chunks = chunks[:5]

    frames_list = []
    params = None

    with tempfile.TemporaryDirectory() as folder:

        for index,chunk in enumerate(chunks):
            result = client.audio.speech.create(
                model=TTS_MODEL,
                voice=FEMALE_VOICE,
                input=chunk,
                response_format="wav"
            )

            path = Path(folder)/f"voice_{index}.wav"
            result.write_to_file(str(path))

            with wave.open(str(path),"rb") as wav:
                current = wav.getparams()
                frames = wav.readframes(wav.getnframes())

            if params is None:
                params = current

            elif (
                current.nchannels != params.nchannels
                or current.sampwidth != params.sampwidth
                or current.framerate != params.framerate
            ):
                raise RuntimeError("Audio format mismatch.")

            frames_list.append(frames)

    output = io.BytesIO()

    with wave.open(output,"wb") as combined:
        combined.setnchannels(params.nchannels)
        combined.setsampwidth(params.sampwidth)
        combined.setframerate(params.framerate)
        combined.writeframes(b"".join(frames_list))

    return output.getvalue(), original_count>5


# =====================================================
# VOICE ASSISTANT PAGE
# =====================================================

def voice_assistant_page():
    header(
        "CyberGuard AI Voice Assistant",
        "Speak naturally, receive an AI answer and listen to a female voice response."
    )

    if "cg_history" not in st.session_state:
        st.session_state.cg_history=[]

    if "cg_answer" not in st.session_state:
        st.session_state.cg_answer=""

    if "cg_transcript" not in st.session_state:
        st.session_state.cg_transcript=""

    if "cg_audio" not in st.session_state:
        st.session_state.cg_audio=None

    left,right = st.columns([1,1.4],gap="large")

    with left:
        st.markdown("""
        <div class="voice-box">
          <div class="voice-orb">🎙️</div>
          <h3 style="text-align:center">Voice Control</h3>
          <p style="text-align:center">Female voice · Hannah</p>
          <div style="text-align:center">
            <span class="tag">Speech Recognition</span>
            <span class="tag">AI Chat</span>
            <span class="tag">Voice Reply</span>
          </div>
        </div>
        """,unsafe_allow_html=True)

        st.markdown("### 1. Record your question")

        st.write(
            "Click the microphone, speak your question and stop recording."
        )

        # Native Streamlit microphone recorder.
        recording = st.audio_input(
            "🎤 Record your voice",
            sample_rate=16000,
            key="cyberguard_audio_input"
        )

        if recording is not None:
            st.audio(recording,format="audio/wav")
            st.success("Recording received.")

            if st.button(
                "✨ Recognize Voice & Ask AI",
                use_container_width=True
            ):
                try:
                    with st.spinner("Recognizing your voice..."):
                        transcript=recognize_voice(recording)

                    st.session_state.cg_transcript=transcript

                    with st.spinner("CyberGuard AI is thinking..."):
                        answer=ask_groq(
                            transcript,
                            st.session_state.cg_history
                        )

                    st.session_state.cg_history.extend([
                        {"role":"user","content":transcript},
                        {"role":"assistant","content":answer}
                    ])

                    st.session_state.cg_answer=answer
                    st.session_state.cg_audio=None

                    st.success("Voice question processed successfully.")
                    st.rerun()

                except Exception as error:
                    st.error(f"Voice processing error: {error}")

                    st.info(
                        "Check microphone permission, Groq API key, internet "
                        "connection and API usage limits."
                    )

        st.markdown("---")
        st.markdown("### 2. Female Voice Response")

        if st.session_state.cg_answer:

            if st.button(
                "🔊 Generate Female Voice",
                use_container_width=True
            ):
                try:
                    with st.spinner("Generating Hannah's female voice..."):
                        audio,truncated=create_female_voice(
                            st.session_state.cg_answer
                        )

                    st.session_state.cg_audio=audio
                    st.session_state.cg_truncated=truncated
                    st.success("Female voice generated.")

                except Exception as error:
                    st.error(f"Voice generation error: {error}")

        if st.session_state.cg_audio:
            st.audio(
                st.session_state.cg_audio,
                format="audio/wav",
                autoplay=False
            )

            if st.session_state.get("cg_truncated",False):
                st.warning(
                    "The spoken response was limited to five speech segments. "
                    "The full answer remains available as text."
                )

    with right:
        st.markdown("### 💬 CyberGuard AI Chat")

        for message in st.session_state.cg_history[-16:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        typed_question=st.chat_input(
            "Ask a cybersecurity question..."
        )

        if typed_question:
            try:
                with st.spinner("CyberGuard AI is responding..."):
                    answer=ask_groq(
                        typed_question,
                        st.session_state.cg_history
                    )

                st.session_state.cg_history.extend([
                    {"role":"user","content":typed_question},
                    {"role":"assistant","content":answer}
                ])

                st.session_state.cg_answer=answer
                st.session_state.cg_audio=None
                st.rerun()

            except Exception as error:
                st.error(f"Chat error: {error}")

        if st.session_state.cg_transcript:
            with st.expander("Latest recognized voice text"):
                st.write(st.session_state.cg_transcript)

        if st.button("🗑️ Clear Conversation",use_container_width=True):
            st.session_state.cg_history=[]
            st.session_state.cg_answer=""
            st.session_state.cg_transcript=""
            st.session_state.cg_audio=None
            st.rerun()

    st.markdown("---")
    st.markdown("### How your voice assistant works")

    steps=st.columns(4)

    descriptions=[
        ("1. Record","Browser microphone records your question."),
        ("2. Transcribe","Groq Whisper converts speech into text."),
        ("3. Respond","GPT-OSS 120B generates the answer."),
        ("4. Speak","Orpheus Hannah creates female speech.")
    ]

    for col,(title,detail) in zip(steps,descriptions):
        with col:
            st.markdown(
                f'<div class="panel"><b>{title}</b><p>{detail}</p></div>',
                unsafe_allow_html=True
            )

    st.caption(
        "Microphone access requires browser permission and a user-initiated "
        "recording. Background Alexa-style wake-word listening is not "
        "supported by this Streamlit implementation."
    )


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:18px 5px">
      <div style="font-size:48px">🛡️</div>
      <div style="font-size:22px;font-weight:800;color:white">
        CYBERGUARD AI
      </div>
      <div style="font-size:10px;letter-spacing:1.5px;color:#8fb8d3">
        INTELLIGENT SECURITY PLATFORM
      </div>
      <p style="color:#9bdcc9;font-size:11px">
        <span class="status-dot"></span> APPLICATION ONLINE
      </p>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("---")
    st.caption("PROJECT MODULES")
    st.caption("Choose a module from the navigation menu.")
    st.markdown("---")
    st.caption("AI · Expert Rules · Threat Analysis")
    st.caption("CyberGuard AI Capstone Project")


# =====================================================
# MULTIPAGE NAVIGATION
# =====================================================

pages=[
    st.Page(dashboard_page,title="Dashboard",icon="🏠",default=True),
    st.Page(threat_analysis_page,title="Threat Analysis",icon="🔍"),
    st.Page(threat_intelligence_page,title="Threat Intelligence",icon="🌐"),
    st.Page(expert_system_page,title="Expert System",icon="🧠"),
    st.Page(ai_prediction_page,title="AI Prediction",icon="🤖"),
    st.Page(workflow_page,title="System Workflow",icon="⚙️"),
    st.Page(reports_page,title="Reports",icon="📊"),
    st.Page(voice_assistant_page,title="Voice Assistant",icon="🎙️")
]

selected=st.navigation(pages,position="sidebar")
selected.run()

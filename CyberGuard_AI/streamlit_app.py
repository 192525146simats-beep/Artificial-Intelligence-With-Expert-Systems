import asyncio
from datetime import datetime, timedelta
from io import BytesIO
import os
import random
import re

import edge_tts
from groq import Groq
import pandas as pd
import plotly.express as px
import streamlit as st


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

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


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
# AI CHAT & VOICE FUNCTIONS
# ==========================================================

SYSTEM_PROMPT = """
You are CyberGuard AI, an intelligent cybersecurity analysis assistant.

Help users understand:
- Malware and ransomware
- Phishing attacks
- Brute-force attacks
- DDoS attacks
- SQL injection
- Suspicious login activity
- MITRE ATT&CK frameworks and incident response playbooks
- Defensive security recommendations

Give clear, practical, and ethical defensive guidance.
Do not claim to have scanned a real network.
"""

VOICE_SYSTEM_PROMPT = """
You are CyberGuard AI, a female cybersecurity voice assistant.
Keep your answers concise, conversational, natural to listen to (3 to 5 sentences max),
and free of markdown symbols like asterisks, hashtags, or bullet points so the speech synthesis sounds completely human.
"""


def ask_groq(question, history=None, voice_mode=False):
    if client is None:
        return (
            "GROQ_API_KEY is missing. Add your Groq API key "
            "in Streamlit Cloud Secrets."
        )

    sys_prompt = VOICE_SYSTEM_PROMPT if voice_mode else SYSTEM_PROMPT
    messages = [{"role": "system", "content": sys_prompt}]

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
            max_completion_tokens=450 if voice_mode else 1400,
        )
        return response.choices[0].message.content or "No response received."

    except Exception as exc:
        return f"AI chat error: {str(exc)}"


# ==========================================================
# FEMALE VOICE GENERATION USING EDGE-TTS
# ==========================================================


async def _generate_edge_tts_async(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    audio_buffer = BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    audio_buffer.seek(0)
    return audio_buffer.getvalue()


def generate_female_audio(
    text: str, voice: str = "en-US-AriaNeural"
) -> bytes:
    """
    Generate natural female neural speech using Edge-TTS.
    """
    clean_text = re.sub(r"[*#_`>-]", "", str(text)).strip()

    if not clean_text:
        raise ValueError("There is no response text to convert to audio.")

    if len(clean_text) > 3000:
        clean_text = clean_text[:3000]

    return asyncio.run(_generate_edge_tts_async(clean_text, voice))


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
            0,
            100,
            5,
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
            "CRITICAL"
            if score >= 80
            else "HIGH"
            if score >= 60
            else "MEDIUM"
            if score >= 30
            else "LOW"
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
# IOC & PHISHING SCANNER (NEW FEATURE)
# ==========================================================


def ioc_scanner_page():
    hero(
        "IOC & Phishing Scanner",
        "Inspect suspicious IP addresses, URLs, file hashes, or email headers.",
    )

    scan_type = st.radio(
        "Select Indicator Type",
        [
            "Suspicious IP / Domain / URL",
            "SHA-256 / MD5 File Hash",
            "Phishing Email / Header Snippet",
        ],
        horizontal=True,
    )

    ioc_input = st.text_area(
        "Paste indicator or suspicious content here:",
        placeholder="e.g., http://secure-login-verify-update.com/auth or 185.220.101.45",
        height=130,
    )

    if st.button("Scan Indicator", use_container_width=True):
        if not ioc_input.strip():
            st.warning("Please enter an indicator or email snippet to scan.")
        else:
            flags = []
            risk_points = 15

            lower_val = ioc_input.lower()
            if any(
                k in lower_val
                for k in ["login", "verify", "urgent", "bank", "update", "free"]
            ):
                flags.append(
                    "High-risk social engineering / credential harvesting keywords detected."
                )
                risk_points += 35
            if "http://" in lower_val:
                flags.append(
                    "Unencrypted HTTP protocol detected (lacks TLS/SSL)."
                )
                risk_points += 20
            if re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", ioc_input):
                flags.append(
                    "Direct IPv4 address reference detected in payload."
                )
                risk_points += 20
            if len(ioc_input.strip()) in (32, 40, 64) and " " not in ioc_input:
                flags.append(
                    "Cryptographic hash format recognized (MD5/SHA-1/SHA-256)."
                )
                risk_points += 25

            risk_points = min(98, risk_points)

            col1, col2 = st.columns(2)
            col1.metric("Heuristic Threat Score", f"{risk_points}/100")
            col2.metric(
                "Classification",
                "Suspicious / Malicious"
                if risk_points >= 55
                else "Low Risk / Benign",
            )

            if flags:
                st.subheader("Detected Risk Indicators")
                for f in flags:
                    st.warning(f)
            else:
                st.success(
                    "No immediate heuristic red flags matched in local pattern rules."
                )

            if client is not None:
                with st.spinner("Running AI Threat Intelligence lookup..."):
                    ai_verdict = ask_groq(
                        f"Analyze this {scan_type} for cybersecurity threats and explain what an analyst should check: {ioc_input[:1000]}"
                    )
                    st.subheader("AI Analyst Assessment")
                    st.markdown(ai_verdict)


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
        mask = (
            filtered.astype(str)
            .apply(lambda col: col.str.contains(search, case=False, na=False))
            .any(axis=1)
        )
        filtered = filtered[mask]

    st.write(f"Records found: {len(filtered)}")

    st.dataframe(
        filtered.sort_values("Risk Score", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.caption("The records shown are synthetic demonstration indicators.")


# ==========================================================
# EXPERT SYSTEM (UPGRADED WITH MITRE ATT&CK + CLI PLAYBOOKS)
# ==========================================================


def expert_system_page():
    hero(
        "Cybersecurity Expert System",
        "Rule-based threat interpretation, MITRE ATT&CK mapping, and response playbooks.",
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
        "Phishing": {
            "mitre": "T1566 - Phishing (Initial Access)",
            "actions": [
                "Do not open suspicious links or attachments.",
                "Verify the sender through a trusted channel.",
                "Block and report the suspicious sender domain.",
                "Reset credentials if they may have been exposed.",
            ],
            "playbook": "# Quarantine email & block sender domain\npostsuper -h <QUEUE_ID>\necho 'malicious-sender.com REJECT' >> /etc/postfix/sender_access",
        },
        "Malware": {
            "mitre": "T1204 - User Execution (Execution)",
            "actions": [
                "Isolate the affected endpoint from the network.",
                "Run an approved endpoint security scan.",
                "Preserve logs and suspicious files for investigation.",
                "Restore from a verified clean backup if necessary.",
            ],
            "playbook": "# Isolate compromised host & kill suspicious PID\niptables -P INPUT DROP && iptables -P OUTPUT DROP\nkill -9 <SUSPICIOUS_PID>",
        },
        "Ransomware": {
            "mitre": "T1486 - Data Encrypted for Impact (Impact)",
            "actions": [
                "Isolate affected systems immediately.",
                "Preserve forensic evidence and volatile memory.",
                "Notify the incident response team.",
                "Restore only from verified clean offline backups.",
            ],
            "playbook": "# Disable SMB shares immediately to stop lateral spread\nsystemctl stop smbd nmbd\nnetsh advfirewall firewall set allprofiles state on",
        },
        "Brute Force": {
            "mitre": "T1110 - Brute Force (Credential Access)",
            "actions": [
                "Block abusive source addresses where appropriate.",
                "Enforce multi-factor authentication.",
                "Apply rate limiting and account lockout policies.",
                "Review authentication logs.",
            ],
            "playbook": "# Block offending IP via UFW / iptables\nufw deny from <SOURCE_IP> to any\nfail2ban-client set sshd banip <SOURCE_IP>",
        },
        "DDoS": {
            "mitre": "T1498 - Network Denial of Service (Impact)",
            "actions": [
                "Activate the organisation's DDoS response plan.",
                "Use approved upstream traffic mitigation.",
                "Monitor service availability.",
                "Contact the hosting or network provider.",
            ],
            "playbook": "# Enable SYN cookies & rate-limit incoming connections\nsysctl -w net.ipv4.tcp_syncookies=1\niptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT",
        },
        "SQL Injection": {
            "mitre": "T1190 - Exploit Public-Facing Application (Initial Access)",
            "actions": [
                "Use parameterised database queries.",
                "Validate and safely handle user input.",
                "Review application and database logs.",
                "Patch the affected application and enable WAF rules.",
            ],
            "playbook": "# Enable ModSecurity WAF blocking mode\nsed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /etc/modsecurity/modsecurity.conf\nsystemctl reload apache2",
        },
        "Suspicious Login": {
            "mitre": "T1078 - Valid Accounts (Persistence / Defense Evasion)",
            "actions": [
                "Verify the login with the account owner.",
                "Review device and location information.",
                "Revoke suspicious sessions and active tokens.",
                "Enable multi-factor authentication.",
            ],
            "playbook": "# Force password reset & invalidate active sessions\npasswd -e <COMPROMISED_USER>\npkill -KILL -u <COMPROMISED_USER>",
        },
    }

    if st.button("Generate Expert Recommendation", use_container_width=True):
        selected = rules[threat]
        st.info(f"**MITRE ATT&CK Mapping:** {selected['mitre']}")

        st.subheader("Recommended Defensive Actions")
        for item in selected["actions"]:
            st.markdown(f"- {item}")

        st.subheader("Automated Incident Response Playbook (CLI)")
        st.code(selected["playbook"], language="bash")


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
        (
            "01",
            "Data Input",
            "Security event, log file, or suspicious activity is entered.",
        ),
        (
            "02",
            "Preprocessing",
            "Input indicators are organised for analysis.",
        ),
        (
            "03",
            "Threat Analysis",
            "Threat characteristics and risk indicators are evaluated.",
        ),
        (
            "04",
            "Expert System",
            "Predefined rules and MITRE ATT&CK mappings generate defensive playbooks.",
        ),
        (
            "05",
            "AI & Voice Assistance",
            "Groq LLM and neural female speech synthesis explain findings interactively.",
        ),
        (
            "06",
            "Reporting",
            "Results are displayed and exported for documentation.",
        ),
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
# REPORTS (UPGRADED WITH CSV LOG UPLOADER)
# ==========================================================


def reports_page():
    hero(
        "Security Reports & Log Ingestion",
        "Upload custom security logs or export the threat-event dataset.",
    )

    uploaded_file = st.file_uploader(
        "Upload Custom Security Log (CSV)",
        type=["csv"],
        help="Upload a CSV file containing security logs to preview and analyze.",
    )

    active_df = df
    if uploaded_file is not None:
        try:
            active_df = pd.read_csv(uploaded_file)
            st.success(
                f"Loaded custom log file: {uploaded_file.name} ({len(active_df)} rows)"
            )
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Events", len(active_df))
    c2.metric(
        "Critical Events",
        int((active_df["Severity"] == "Critical").sum())
        if "Severity" in active_df.columns
        else "N/A",
    )
    c3.metric(
        "Blocked Events",
        int((active_df["Status"] == "Blocked").sum())
        if "Status" in active_df.columns
        else "N/A",
    )

    st.subheader("Threat Event Report")

    display_df = (
        active_df.sort_values("Timestamp", ascending=False)
        if "Timestamp" in active_df.columns
        else active_df
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download CSV Report",
        data=active_df.to_csv(index=False).encode("utf-8"),
        file_name="cyberguard_threat_report.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ==========================================================
# AI ASSISTANT (GROQ CHATBOT)
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
                    voice_mode=False,
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
# SPEECH-TO-SPEECH FEMALE VOICE ASSISTANT
# ==========================================================


def voice_assistant_page():
    hero(
        "CyberGuard Speech-to-Speech Assistant",
        "Speak directly to CyberGuard AI and receive an instant spoken female voice response.",
    )

    if client is None:
        st.error(
            "GROQ_API_KEY is missing. Add it in Streamlit Cloud Secrets."
        )
        return

    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []

    if "last_processed_audio" not in st.session_state:
        st.session_state.last_processed_audio = None

    if "latest_voice_reply_audio" not in st.session_state:
        st.session_state.latest_voice_reply_audio = None

    # Female Voice Accent Selector
    voice_choice = st.selectbox(
        "Select Female Assistant Voice",
        options=[
            "en-US-AriaNeural (US English - Female)",
            "en-IN-NeerjaNeural (Indian English - Female)",
            "en-GB-SoniaNeural (British English - Female)",
        ],
        index=0,
    )
    selected_voice_id = voice_choice.split(" ")[0]

    st.markdown("---")
    st.subheader("🎙️ Speak to CyberGuard AI")
    st.caption(
        "Click the microphone icon below to record your question. Once you stop recording, CyberGuard AI will automatically reply by voice."
    )

    audio_file = st.audio_input(
        "Record your voice query",
        sample_rate=16000,
        key="cyberguard_s2s_audio",
    )

    # Automatically trigger Speech -> AI -> Female Speech when new audio is recorded
    if audio_file is not None:
        audio_bytes = audio_file.getvalue()

        if audio_bytes != st.session_state.last_processed_audio:
            st.session_state.last_processed_audio = audio_bytes

            try:
                with st.spinner("Listening & thinking..."):
                    # 1. Speech to Text via Groq Whisper
                    transcript = client.audio.transcriptions.create(
                        model=STT_MODEL,
                        file=(
                            "cyberguard_recording.wav",
                            audio_bytes,
                            "audio/wav",
                        ),
                        response_format="json",
                    )

                    question = transcript.text.strip()

                    if not question:
                        st.warning(
                            "No speech was detected. Please try speaking again."
                        )
                    else:
                        # 2. AI Reasoning via Groq
                        answer = ask_groq(
                            question,
                            st.session_state.voice_history,
                            voice_mode=True,
                        )

                        st.session_state.voice_history.extend([
                            {"role": "user", "content": question},
                            {"role": "assistant", "content": answer},
                        ])

                        # 3. Text to Natural Female Speech via Edge-TTS
                        reply_audio = generate_female_audio(
                            answer, voice=selected_voice_id
                        )
                        st.session_state.latest_voice_reply_audio = reply_audio

            except Exception as exc:
                st.error(f"Speech-to-Speech error: {str(exc)}")

    # Autoplay the female voice response directly (pure speech-to-speech experience)
    if st.session_state.latest_voice_reply_audio is not None:
        st.success("🔊 CyberGuard AI Response:")
        st.audio(
            st.session_state.latest_voice_reply_audio,
            format="audio/mp3",
            autoplay=True,
        )

    st.write("")
    if st.button("Reset Voice Session"):
        st.session_state.voice_history = []
        st.session_state.last_processed_audio = None
        st.session_state.latest_voice_reply_audio = None
        st.rerun()


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
    st.Page(ioc_scanner_page, title="IOC & Phishing Scanner", icon="🧪"),
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

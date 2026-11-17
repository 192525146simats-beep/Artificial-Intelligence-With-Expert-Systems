
import streamlit as st
import pandas as pd
import plotly.express as px

from cyberguard.analysis import analyse_events
from cyberguard.threat_intelligence import THREAT_DATABASE
from cyberguard.voice_assistant import listen, speak, get_response

st.set_page_config(
    page_title="CyberGuard AI",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

.stApp {
    background:
    radial-gradient(circle at top right,#123c60,#071426 55%);
    color:#eaf4ff;
    font-family:Manrope,sans-serif;
}

section[data-testid="stSidebar"] {
    background:#0b1e35;
    border-right:1px solid #174a70;
}

.block-container {
    padding-top:2rem;
    max-width:1500px;
}

.hero {
    background:linear-gradient(110deg,#102d4d,#123e5b);
    border:1px solid #23759b;
    border-radius:20px;
    padding:28px;
    animation:appear .8s ease;
}

.hero h1 {
    font-size:38px;
    color:#ffffff;
}

.hero p {
    color:#a9d5ef;
}

@keyframes appear {
    from {opacity:0;transform:translateY(15px);}
    to {opacity:1;transform:translateY(0);}
}

.metric-card {
    background:linear-gradient(145deg,#142d49,#0c2038);
    border:1px solid #285274;
    border-top:3px solid #00d9ff;
    border-radius:15px;
    padding:20px;
    min-height:125px;
    transition:transform .25s;
}

.metric-card:hover {
    transform:translateY(-5px);
}

.metric-title {
    color:#8eb4d3;
    font-size:12px;
    letter-spacing:2px;
}

.metric-number {
    font-size:32px;
    font-weight:800;
    color:white;
}

.metric-sub {
    color:#8eb4d3;
    font-size:12px;
}

.panel {
    background:#10243b;
    border:1px solid #264a68;
    border-radius:16px;
    padding:20px;
}

h1,h2,h3 {
    color:#f1f7ff;
}

.stButton>button {
    background:linear-gradient(90deg,#007dba,#00b9d2);
    color:white;
    border:0;
    border-radius:10px;
    font-weight:bold;
}

.stButton>button:hover {
    background:#00a9d0;
    color:white;
}
</style>
""", unsafe_allow_html=True)


def hero(title, description):
    st.markdown(f"""
    <div class="hero">
      <div style="color:#39d9ed;letter-spacing:3px">
        CYBERGUARD AI / SECURITY OPERATIONS
      </div>
      <h1>{title}</h1>
      <p>{description}</p>
      <div style="color:#48d8e9">
        DETECT &nbsp; • &nbsp; ANALYSE &nbsp; • &nbsp; PREVENT
      </div>
    </div>
    """, unsafe_allow_html=True)


def metric(title, number, subtitle):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-title">{title}</div>
      <div class="metric-number">{number}</div>
      <div class="metric-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def sample_data():
    try:
        return pd.read_csv(
            "data/sample_security_events.csv"
        )
    except FileNotFoundError:
        return pd.DataFrame([
            ["E001","192.0.2.10","198.51.100.5","TCP",443,18000,1,35],
            ["E002","203.0.113.8","198.51.100.5","TCP",22,1200,14,18],
            ["E003","192.0.2.45","198.51.100.9","UDP",53,800,0,920],
            ["E004","203.0.113.22","198.51.100.2","TCP",3389,900,11,12],
            ["E005","192.0.2.88","198.51.100.3","TCP",443,88000000,0,28]
        ], columns=[
            "event_id","src_ip","dst_ip","protocol",
            "dst_port","bytes","failed_logins",
            "requests_per_minute"
        ])


if "data" not in st.session_state:
    st.session_state.data = sample_data()

with st.sidebar:

    st.markdown("""
    <h1 style="color:#35d9ed">🛡️ CyberGuard AI</h1>
    <p style="font-size:11px;color:#91b9d7">
    INTELLIGENT CYBER THREAT ANALYSIS
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Threat Analysis",
            "Threat Intelligence",
            "Expert System",
            "AI Prediction",
            "System Workflow",
            "Security Reports",
            "Voice Assistant"
        ]
    )

    st.markdown("---")
    st.success("Analysis engine ready")
    st.caption("Academic Capstone Prototype")

results = analyse_events(st.session_state.data)

critical = int((results.severity == "Critical").sum())
high = int((results.severity == "High").sum())
medium = int((results.severity == "Medium").sum())
low = int((results.severity == "Low").sum())


# DASHBOARD

if page == "Dashboard":

    hero(
        "Cyber Threat Command Center",
        "Intelligent monitoring, AI threat prediction and expert-system analysis."
    )

    st.write("")

    c1,c2,c3,c4 = st.columns(4)

    with c1:
        metric("THREATS DETECTED",len(results),"Events analysed")

    with c2:
        metric("CRITICAL THREATS",critical,"Immediate review")

    with c3:
        metric("HIGH RISK",high,"Priority investigation")

    with c4:
        metric("LOW RISK",low,"Routine monitoring")

    st.write("")

    left,right = st.columns([1.1,1])

    with left:
        st.markdown(
            '<div class="panel"><h3>Threat Severity Overview</h3>',
            unsafe_allow_html=True
        )

        chart = results["severity"].value_counts().reset_index()
        chart.columns = ["Severity","Count"]

        fig = px.pie(
            chart,
            names="Severity",
            values="Count",
            hole=0.65,
            color="Severity",
            color_discrete_map={
                "Critical":"#ff4d6d",
                "High":"#ff9b54",
                "Medium":"#f4d35e",
                "Low":"#26c6a0"
            }
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(fig,use_container_width=True)
        st.markdown("</div>",unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="panel"><h3>Threat Categories</h3>',
            unsafe_allow_html=True
        )

        chart2 = results["threat_type"].value_counts().reset_index()
        chart2.columns = ["Threat","Count"]

        fig2 = px.bar(
            chart2,
            x="Threat",
            y="Count",
            color="Count",
            color_continuous_scale="teal"
        )

        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(fig2,use_container_width=True)
        st.markdown("</div>",unsafe_allow_html=True)

    st.subheader("Recent Security Events")

    st.dataframe(results,use_container_width=True,hide_index=True)


# THREAT ANALYSIS

elif page == "Threat Analysis":

    hero(
        "Threat Analysis",
        "Upload security events and analyse suspicious activity."
    )

    uploaded = st.file_uploader(
        "Upload security CSV",
        type=["csv"]
    )

    if uploaded:
        try:
            st.session_state.data = pd.read_csv(uploaded)
            results = analyse_events(st.session_state.data)
            st.success("File analysed successfully.")
        except Exception as error:
            st.error(f"Unable to analyse file: {error}")

    st.dataframe(
        analyse_events(st.session_state.data),
        use_container_width=True,
        hide_index=True
    )


# THREAT INTELLIGENCE

elif page == "Threat Intelligence":

    hero(
        "Threat Intelligence Center",
        "Explore common cyber threats, their indicators and prevention."
    )

    for name, info in THREAT_DATABASE.items():

        with st.expander(name):

            st.write("**Description**")
            st.write(info["description"])

            st.write("**Indicators**")
            st.write(info["indicators"])

            st.write("**Prevention**")
            st.write(info["prevention"])


# EXPERT SYSTEM

elif page == "Expert System":

    hero(
        "Expert System",
        "Explainable knowledge-based threat identification."
    )

    st.write(
        "The expert system uses predefined IF–THEN rules "
        "to evaluate suspicious security events."
    )

    st.dataframe(
        results[[
            "event_id",
            "threat_type",
            "severity",
            "rule_matches",
            "recommendation"
        ]],
        use_container_width=True,
        hide_index=True
    )


# AI PREDICTION

elif page == "AI Prediction":

    hero(
        "AI Threat Prediction",
        "Machine-learning-based classification of suspicious events."
    )

    st.warning(
        "The model uses synthetic training data for academic "
        "demonstration. Predictions are not production security verdicts."
    )

    st.dataframe(
        results[[
            "event_id",
            "threat_type",
            "confidence",
            "risk_score"
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.metric(
        "Average model confidence",
        f"{results.confidence.mean():.2f}%"
    )


# WORKFLOW

elif page == "System Workflow":

    hero(
        "System Workflow",
        "How CyberGuard AI processes and analyses security events."
    )

    stages = [
        ("01","DATA COLLECTION","Upload network security logs"),
        ("02","PREPROCESSING","Clean and prepare event features"),
        ("03","AI ANALYSIS","Random Forest threat classification"),
        ("04","EXPERT SYSTEM","Evaluate IF–THEN knowledge rules"),
        ("05","RISK ASSESSMENT","Calculate severity and risk score"),
        ("06","RESULTS","Generate alerts and reports")
    ]

    for number,title,description in stages:

        st.markdown(f"""
        <div class="panel" style="margin:12px 0">
            <h3 style="color:#35d9ed">{number} — {title}</h3>
            <p>{description}</p>
        </div>
        """,unsafe_allow_html=True)

        if number != "06":
            st.markdown(
                "<div style='text-align:center;color:#35d9ed'>↓</div>",
                unsafe_allow_html=True
            )

    st.subheader("System Architecture")

    st.code("""
Security Event Input
        |
        v
Data Preprocessing
        |
   +----+----+
   |         |
   v         v
AI Model   Expert Rules
   |         |
   +----+----+
        |
        v
Risk Assessment
        |
        v
Dashboard / Alerts / Reports
    """,language="text")


# REPORTS

elif page == "Security Reports":

    hero(
        "Security Reports",
        "Review and export threat analysis results."
    )

    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True
    )

    csv = results.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV Report",
        data=csv,
        file_name="CyberGuard_Report.csv",
        mime="text/csv"
    )


# VOICE ASSISTANT

elif page == "Voice Assistant":

    hero(
        "CyberGuard Voice Assistant",
        "Interact with your cybersecurity expert system using voice."
    )

    st.markdown(
        '<div class="panel"><h2>🎙️ Voice Control</h2>'
        '<p>Ask about threats, reports and system workflow.</p></div>',
        unsafe_allow_html=True
    )

    spoken = listen()

    if spoken:

        st.success(f"You said: {spoken}")

        answer = get_response(spoken,results)

        st.info(answer)

        audio = speak(answer)

        if audio:
            st.audio(audio,format="audio/mp3")

    st.markdown("### Try these commands")

    st.markdown("""
    - Give me the security summary.
    - Explain phishing.
    - What is ransomware?
    - Explain the system workflow.
    - Generate a threat report.
    """)


st.markdown("""
<div style="text-align:center;color:#6688a8;padding:30px">
CYBERGUARD AI | INTELLIGENT CYBER THREAT ANALYSIS EXPERT SYSTEM
<br>
Artificial Intelligence and Expert Systems Capstone Project
</div>
""",unsafe_allow_html=True)

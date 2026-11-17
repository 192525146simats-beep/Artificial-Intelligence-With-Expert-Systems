
import streamlit as st
import plotly.express as px

def render(results):
    st.title("🛡️ Cyber Threat Command Center")
    st.caption("AI-powered cybersecurity monitoring")

    total = len(results)
    critical = (results.severity == "Critical").sum()
    high = (results.severity == "High").sum()
    low = (results.severity == "Low").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Events Analysed", total)
    c2.metric("Critical Threats", int(critical))
    c3.metric("High Risk", int(high))
    c4.metric("Low Risk", int(low))

    left, right = st.columns(2)

    with left:
        st.subheader("Threat Severity")
        counts = results.severity.value_counts().reset_index()
        counts.columns = ["Severity", "Count"]
        fig = px.pie(
            counts,
            names="Severity",
            values="Count",
            hole=0.6,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Threat Categories")
        counts = results.threat_type.value_counts().reset_index()
        counts.columns = ["Threat", "Count"]
        fig = px.bar(
            counts,
            x="Threat",
            y="Count",
            color="Threat",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Security Events")
    st.dataframe(results, use_container_width=True)

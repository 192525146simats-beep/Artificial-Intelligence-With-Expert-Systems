
import streamlit as st
from cyberguard.rules import THREAT_RULES

def render(results):
    st.title("🧠 Expert System")
    st.write("Knowledge-based cyber threat identification.")

    st.subheader("Expert Knowledge Base")

    for name, rule in THREAT_RULES.items():
        with st.expander(name):
            st.write("Severity:", rule["severity"])
            st.write("Recommendation:")
            st.write(rule["recommendation"])

    st.subheader("Triggered Expert Rules")

    st.dataframe(
        results[[
            "event_id",
            "threat_type",
            "severity",
            "rule_matches",
            "recommendation"
        ]],
        use_container_width=True
    )


import streamlit as st
from cyberguard.threat_intelligence import THREAT_DATABASE


def render():

    st.title("🧬 Cyber Threat Intelligence")

    st.write(
        "Understand different cybersecurity attacks, "
        "their characteristics, warning indicators and prevention."
    )

    search = st.text_input(
        "Search a cyber threat",
        placeholder="Example: Phishing"
    )

    for name, details in THREAT_DATABASE.items():

        if search and search.lower() not in name.lower():
            continue

        with st.expander(f"🛡️ {name}"):

            st.markdown("### Threat Description")
            st.write(details["description"])

            st.markdown("### Warning Indicators")
            st.write(details["indicators"])

            st.markdown("### Prevention Methods")
            st.success(details["prevention"])

    st.divider()

    st.subheader("Cybersecurity Best Practices")

    practices = [
        "Enable multi-factor authentication.",
        "Use strong and unique passwords.",
        "Update operating systems and software.",
        "Avoid suspicious links and attachments.",
        "Maintain regular and tested backups.",
        "Monitor unusual network traffic.",
        "Restrict access using least privilege."
    ]

    for practice in practices:
        st.markdown(f"✅ {practice}")

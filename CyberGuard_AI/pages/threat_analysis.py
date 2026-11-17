
import streamlit as st
import pandas as pd
from cyberguard.analysis import analyse_events

def render(current_data):
    st.title("🔍 Cyber Threat Analysis")

    st.write(
        "Upload network security logs to identify "
        "potential cyber threats."
    )

    uploaded = st.file_uploader(
        "Upload Security CSV",
        type=["csv"]
    )

    if uploaded:
        try:
            current_data = pd.read_csv(uploaded)
            st.session_state["cyberguard_data"] = current_data
            st.success("Security data uploaded successfully.")
        except Exception as e:
            st.error(str(e))
            return

    if current_data is not None:
        results = analyse_events(current_data)

        st.subheader("Analysis Results")
        st.dataframe(results, use_container_width=True)

        st.download_button(
            "Download Analysis",
            results.to_csv(index=False),
            "threat_analysis.csv",
            "text/csv"
        )

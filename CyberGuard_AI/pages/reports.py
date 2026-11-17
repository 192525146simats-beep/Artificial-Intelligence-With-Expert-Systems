
import streamlit as st
from datetime import datetime

def render(results):
    st.title("📊 Security Reports")

    st.write("Cybersecurity analysis and reporting centre.")

    if results.empty:
        st.info("No security events available.")
        return

    st.metric("Total Events", len(results))

    st.dataframe(
        results,
        use_container_width=True
    )

    csv_data = results.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download CSV Report",
        csv_data,
        file_name=(
            f"CyberGuard_Report_"
            f"{datetime.now():%Y%m%d_%H%M}.csv"
        ),
        mime="text/csv"
    )

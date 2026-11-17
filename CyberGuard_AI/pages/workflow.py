
import streamlit as st

def render():
    st.title("🔄 System Workflow")

    stages = [
        ("01", "Data Collection",
         "Import network logs and security events."),
        ("02", "Data Preprocessing",
         "Clean records and extract important features."),
        ("03", "AI Analysis",
         "Random Forest identifies potential threats."),
        ("04", "Expert System",
         "IF-THEN rules identify suspicious patterns."),
        ("05", "Risk Assessment",
         "Calculate risk scores and threat severity."),
        ("06", "Report Generation",
         "Display findings and export security reports.")
    ]

    for number, title, description in stages:
        st.markdown(
            f"""
            <div style="
                background:#102b45;
                padding:20px;
                margin:10px 0;
                border-left:5px solid #00d9ff;
                border-radius:12px;
                animation: fadeIn 0.7s ease;
            ">
                <h3 style="color:#00d9ff">
                    {number} - {title}
                </h3>
                <p style="color:white">
                    {description}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='text-align:center;color:#00d9ff'>↓</div>",
            unsafe_allow_html=True
        )

    st.subheader("System Architecture")

    st.code("""
        Security Event Input
                |
                v
        Data Preprocessing
                |
          +-----+-----+
          |           |
          v           v
        AI Model   Expert Rules
          |           |
          +-----+-----+
                |
                v
         Risk Assessment
                |
                v
         Dashboard and Reports
    """)

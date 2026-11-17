
import streamlit as st
from cyberguard.prediction import predict_threat, train_model

def render(results):
    st.title("🤖 AI Threat Prediction")

    st.write(
        "Random Forest machine learning model "
        "for cybersecurity threat classification."
    )

    st.warning(
        "This academic prototype uses synthetic training data."
    )

    if st.button("Train AI Model"):
        with st.spinner("Training model..."):
            _, accuracy = train_model()

        st.success(
            f"Synthetic test accuracy: {accuracy:.2%}"
        )

    st.subheader("Manual Threat Prediction")

    with st.form("prediction_form"):
        port = st.number_input(
            "Destination Port", 0, 65535, 443
        )
        byte_count = st.number_input(
            "Bytes Transferred", 0, value=18000
        )
        failed = st.number_input(
            "Failed Login Attempts", 0, value=0
        )
        requests = st.number_input(
            "Requests Per Minute", 0, value=35
        )

        submit = st.form_submit_button("Predict Threat")

    if submit:
        prediction, confidence = predict_threat(
            port,
            byte_count,
            failed,
            requests
        )

        st.success(f"Predicted Threat: {prediction}")
        st.metric(
            "Model Confidence",
            f"{confidence:.2f}%"
        )

    st.subheader("Dataset Predictions")
    st.dataframe(
        results[[
            "event_id",
            "threat_type",
            "confidence",
            "risk_score"
        ]],
        use_container_width=True
    )

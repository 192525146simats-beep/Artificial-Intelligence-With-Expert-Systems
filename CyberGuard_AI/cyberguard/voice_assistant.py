
from io import BytesIO
from gtts import gTTS


def listen():
    try:
        from streamlit_mic_recorder import speech_to_text

        return speech_to_text(
            language="en",
            start_prompt="🎙️ Start speaking",
            stop_prompt="⏹️ Stop",
            just_once=True,
            key="cyberguard_voice"
        )

    except ImportError:
        return None


def speak(text):
    try:
        audio = BytesIO()

        tts = gTTS(
            text=text,
            lang="en",
            slow=False
        )

        tts.write_to_fp(audio)
        audio.seek(0)

        return audio

    except Exception:
        return None


def get_response(command, results):

    command = command.lower()

    critical = int(
        (results["severity"] == "Critical").sum()
    )

    high = int(
        (results["severity"] == "High").sum()
    )

    if "summary" in command or "dashboard" in command:
        return (
            f"CyberGuard analysed {len(results)} events. "
            f"There are {critical} critical threats and "
            f"{high} high severity threats."
        )

    if "phishing" in command:
        return (
            "Phishing is a cyber attack that uses fraudulent "
            "messages and websites to steal sensitive information."
        )

    if "ransomware" in command:
        return (
            "Ransomware is malicious software that encrypts "
            "files and demands payment."
        )

    if "workflow" in command:
        return (
            "The workflow includes data collection, preprocessing, "
            "AI classification, expert system evaluation, "
            "risk assessment and report generation."
        )

    if "report" in command:
        return (
            "Open the Security Reports section to download "
            "your current analysis results."
        )

    if "threat" in command:
        return (
            f"The current dataset contains {len(results)} events. "
            f"{critical} are critical and {high} are high severity."
        )

    return (
        "I can explain cyber threats, dashboard statistics, "
        "security workflow and analysis reports. "
        "Please try another command."
    )

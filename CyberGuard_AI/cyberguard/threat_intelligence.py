
THREAT_DATABASE = {
    "Phishing": {
        "description":
            "Fraudulent messages and websites designed to steal "
            "credentials or confidential information.",
        "indicators":
            "Suspicious URLs, fake sender addresses, unexpected "
            "attachments and urgent requests.",
        "prevention":
            "Verify senders, avoid suspicious links and enable MFA."
    },

    "Ransomware": {
        "description":
            "Malware that encrypts or blocks access to data "
            "and demands payment.",
        "indicators":
            "Unexpected file encryption, unusual file extensions "
            "and suspicious processes.",
        "prevention":
            "Maintain secure backups, update systems and "
            "restrict user privileges."
    },

    "DDoS": {
        "description":
            "Distributed denial of service attacks overwhelm "
            "network resources with traffic.",
        "indicators":
            "Unusual traffic spikes, high request rates "
            "and service interruptions.",
        "prevention":
            "Use traffic filtering, rate limiting and DDoS protection."
    },

    "Brute Force": {
        "description":
            "Repeated password attempts intended to gain "
            "unauthorised account access.",
        "indicators":
            "Repeated login failures and suspicious authentication.",
        "prevention":
            "Use MFA, strong passwords and login rate limiting."
    },

    "Port Scanning": {
        "description":
            "Network reconnaissance that checks which services "
            "and ports are accessible.",
        "indicators":
            "Repeated connection attempts to different ports.",
        "prevention":
            "Restrict exposed services and monitor firewall logs."
    },

    "Data Exfiltration": {
        "description":
            "Unauthorised movement of confidential information "
            "outside an organisation.",
        "indicators":
            "Unusual outbound transfers and unknown destinations.",
        "prevention":
            "Monitor outbound traffic and apply access controls."
    }
}

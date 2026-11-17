
THREAT_RULES = {
    "Brute Force": {
        "condition": "failed_logins >= 8",
        "severity": "High",
        "recommendation": "Enable MFA and restrict repeated login attempts."
    },
    "DDoS": {
        "condition": "requests_per_minute >= 600",
        "severity": "Critical",
        "recommendation": "Apply rate limiting and investigate traffic sources."
    },
    "Data Exfiltration": {
        "condition": "bytes >= 50000000",
        "severity": "High",
        "recommendation": "Investigate large outbound data transfers."
    },
    "Port Scanning": {
        "condition": "dst_port in [21, 22, 3389, 445]",
        "severity": "Medium",
        "recommendation": "Validate exposed services and review firewall logs."
    }
}


def evaluate_rules(row):
    alerts = []

    failed = float(row.get("failed_logins", 0))
    requests = float(row.get("requests_per_minute", 0))
    size = float(row.get("bytes", 0))
    port = int(row.get("dst_port", 0))

    if failed >= 8:
        alerts.append("Brute Force")

    if requests >= 600:
        alerts.append("DDoS")

    if size >= 50_000_000:
        alerts.append("Data Exfiltration")

    if port in [21, 22, 3389, 445]:
        alerts.append("Port Scanning")

    return alerts


def get_recommendations(alerts):
    return [
        THREAT_RULES[name]["recommendation"]
        for name in alerts
    ]

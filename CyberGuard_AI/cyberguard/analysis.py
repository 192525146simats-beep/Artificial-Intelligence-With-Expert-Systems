
import pandas as pd

from cyberguard.rules import (
    evaluate_rules,
    get_recommendations
)
from cyberguard.prediction import predict_threat


def analyse_events(df):

    df = df.copy()

    defaults = {
        "event_id": "Unknown",
        "src_ip": "Unknown",
        "dst_ip": "Unknown",
        "protocol": "TCP",
        "dst_port": 0,
        "bytes": 0,
        "failed_logins": 0,
        "requests_per_minute": 0
    }

    for column, default in defaults.items():
        if column not in df.columns:
            df[column] = default

    numeric = [
        "dst_port",
        "bytes",
        "failed_logins",
        "requests_per_minute"
    ]

    for column in numeric:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        ).fillna(0)

    results = []

    for index, row in df.iterrows():

        alerts = evaluate_rules(row)

        prediction, confidence = predict_threat(
            int(row["dst_port"]),
            int(row["bytes"]),
            int(row["failed_logins"]),
            int(row["requests_per_minute"])
        )

        score = (
            min(int(row["failed_logins"]), 20) * 3
            + min(int(row["requests_per_minute"]), 1500) / 15
            + (25 if row["bytes"] >= 50000000 else 0)
            + (15 if int(row["dst_port"]) in
               [21, 22, 3389, 445] else 0)
        )

        score = min(int(score), 100)

        if len(alerts) >= 3:
            severity = "Critical"
        elif len(alerts) >= 2 or score >= 65:
            severity = "High"
        elif len(alerts) == 1 or score >= 25:
            severity = "Medium"
        else:
            severity = "Low"

        recommendations = get_recommendations(alerts)

        results.append({
            "event_id": row["event_id"],
            "src_ip": row["src_ip"],
            "dst_ip": row["dst_ip"],
            "threat_type": prediction,
            "severity": severity,
            "risk_score": score,
            "confidence": confidence,
            "rule_matches": ", ".join(alerts) if alerts else "None",
            "recommendation": "; ".join(recommendations)
                if recommendations else
                "Continue routine monitoring"
        })

    return pd.DataFrame(results)


import os
import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


MODEL_PATH = "models/threat_model.pkl"


def create_training_data():
    np.random.seed(42)

    normal = np.column_stack([
        np.random.randint(80, 500, 300),
        np.random.randint(100, 50000, 300),
        np.random.randint(0, 3, 300),
        np.random.randint(1, 100, 300)
    ])

    brute = np.column_stack([
        np.random.randint(20, 200, 200),
        np.random.randint(100, 5000, 200),
        np.random.randint(8, 25, 200),
        np.random.randint(1, 100, 200)
    ])

    ddos = np.column_stack([
        np.random.randint(80, 500, 200),
        np.random.randint(1000, 50000, 200),
        np.random.randint(0, 3, 200),
        np.random.randint(600, 2000, 200)
    ])

    exfiltration = np.column_stack([
        np.random.randint(80, 500, 200),
        np.random.randint(50000000, 150000000, 200),
        np.random.randint(0, 3, 200),
        np.random.randint(1, 100, 200)
    ])

    X = np.vstack([normal, brute, ddos, exfiltration])

    y = np.array(
        ["Normal"] * 300 +
        ["Brute Force"] * 200 +
        ["DDoS"] * 200 +
        ["Data Exfiltration"] * 200
    )

    return X, y


def train_model():
    X, y = create_training_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    accuracy = accuracy_score(
        y_test,
        model.predict(X_test)
    )

    os.makedirs("models", exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    return model, accuracy


def load_model():
    if not os.path.exists(MODEL_PATH):
        model, accuracy = train_model()
        return model, accuracy

    return joblib.load(MODEL_PATH), None


def predict_threat(dst_port, bytes_sent,
                   failed_logins, requests_per_minute):

    model, accuracy = load_model()

    features = np.array([[
        dst_port,
        bytes_sent,
        failed_logins,
        requests_per_minute
    ]])

    prediction = model.predict(features)[0]

    probabilities = model.predict_proba(features)[0]
    confidence = max(probabilities) * 100

    return prediction, round(confidence, 2)

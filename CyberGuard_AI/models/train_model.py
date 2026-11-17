
from pathlib import Path
import sys

# Add the main project directory to Python's module path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cyberguard.prediction import train_model


if __name__ == "__main__":

    print("Starting CyberGuard AI model training...")

    model, accuracy = train_model()

    print("Model training completed.")
    print(f"Synthetic test accuracy: {accuracy:.2%}")

    model_path = PROJECT_ROOT / "models" / "threat_model.pkl"

    print(f"Model saved at: {model_path}")

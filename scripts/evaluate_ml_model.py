
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, f1_score, recall_score, precision_score, accuracy_score

def evaluate_model():

    # 1. Generate Training Data (Normal Behavior)
    # Simulate 200 samples of "Normal" CPU (10-40%) and RAM (30-60%)
    rng = np.random.RandomState(42)
    X_train = np.r_[
        rng.uniform(low=10, high=40, size=(100, 1)),  # CPU
        rng.uniform(low=30, high=60, size=(100, 1))   # RAM
    ].reshape(100, 2)

    # 2. Generate Test Data (Mixed)
    # 80 "Normal" samples
    X_test_normal = np.r_[
        rng.uniform(low=10, high=40, size=(80, 1)),
        rng.uniform(low=30, high=60, size=(80, 1))
    ].reshape(80, 2)
    
    # 20 "Anomaly" samples (Crypto Miner: CPU 90-100%)
    X_test_anomaly = np.r_[
        rng.uniform(low=90, high=100, size=(20, 1)),
        rng.uniform(low=30, high=60, size=(20, 1))
    ].reshape(20, 2)

    X_test = np.vstack([X_test_normal, X_test_anomaly])
    
    # Ground Truth Labels: 1 for Normal, -1 for Anomaly
    y_true = np.array([1] * 80 + [-1] * 20)

    clf = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    clf.fit(X_train)
    y_pred = clf.predict(X_test)

    # Calculate Metrics
    # Note: Pos Label is -1 (Anomaly) for our context of "Detecting Threats"
    # But sklearn report treats 1 as default pos label usually. 
    # Let's print full report.
    
    # Calculate Metrics
    precision = precision_score(y_true, y_pred, pos_label=-1)
    recall = recall_score(y_true, y_pred, pos_label=-1)
    f1 = f1_score(y_true, y_pred, pos_label=-1)
    accuracy = accuracy_score(y_true, y_pred)

    print(f"Accuracy:  {accuracy:.2%}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall:    {recall:.2f}")
    print(f"F1 Score:  {f1:.2f}")

if __name__ == "__main__":
    evaluate_model()

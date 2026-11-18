# MLA0103 - Artificial Intelligence and Expert System Laboratory

This repository contains the complete coursework, laboratory experiments, and capstone project for **MLA01 - Artificial Intelligence and Expert Systems**.

---

## Laboratory Experiments (MLA0103)

A collection of 27 foundational programs covering search algorithms, game playing, constraint satisfaction, machine learning, and rule-based expert systems:

1. **01. BFS** – Breadth-First Search *(Uninformed Search)*
2. **02. DFS** – Depth-First Search *(Uninformed Search)*
3. **03. UCS** – Uniform Cost Search *(Uninformed Search)*
4. **04. Best First** – Best-First Search *(Informed / Heuristic Search)*
5. **05. Greedy Search** – Greedy Best-First Search *(Informed / Heuristic Search)*
6. **06. A* Search** – A* Search Algorithm *(Informed / Heuristic Search)*
7. **07. Minimax** – Minimax Algorithm *(Adversarial Search / Game Playing)*
8. **08. Alpha Beta** – Alpha-Beta Pruning *(Adversarial Search / Game Playing)*
9. **09. Water Jug** – Water Jug Problem *(State-Space Search)*
10. **10. Hanoi** – Tower of Hanoi *(State-Space Search / Recursion)*
11. **11. Crypt Arithmetic** – Cryptarithmetic Puzzle *(Constraint Satisfaction Problem)*
12. **12. Decision Tree** – Decision Tree Classifier *(Machine Learning)*
13. **13. Neural Network** – Artificial Neural Network *(Deep Learning)*
14. **14. Diet Expert** – Diet Recommendation System *(Rule-Based Expert System)*
15. **15. Family Knowledge** – Family Knowledge Base *(Knowledge Representation & Logic)*
16. **16. Birds Fly** – Default Reasoning *(Non-Monotonic Reasoning)*
17. **17. Medical Expert** – Medical Diagnosis System *(Rule-Based Expert System)*
18. **18. Fruit Color** – Fruit Color Identification *(Knowledge Representation / Rule Matching)*
19. **19. Planet Facts** – Planet Facts Knowledge Base *(Knowledge Representation)*
20. **20. Person DOB** – Person Date of Birth Retrieval *(Fact Retrieval & Logic Programming)*
21. **21. Pattern Recognition** – Pattern Recognition *(Machine Learning / Classification)*
22. **22. Monkey Banana** – Monkey and Banana Problem *(Planning & State-Space Search)*
23. **23. Forward Chaining** – Forward Chaining Inference *(Inference Engine / Logic)*
24. **24. Backward Chaining** – Backward Chaining Inference *(Inference Engine / Logic)*
25. **25. Prolog Style Search** – Prolog-Style Search *(Logic Programming & Backtracking)*
26. **26. Recursive Sum** – Recursive Sum Calculation *(Logic Programming / Recursion)*
27. **27. Vowel Identification** – Vowel Identification *(Pattern Matching / Logic)*

---

## Capstone Project: CyberGuard AI

### Intelligent Cyber Threat Analysis Expert System
An AI-powered expert system designed to analyze cybersecurity events, detect suspicious behavior, classify potential cyber threats, and recommend actionable security measures.

🔗 **Live Application:** [Launch CyberGuard AI on Streamlit](https://cyber-threat-analyzer.streamlit.app/)

#### Key Features & Modules
1. **Command Dashboard** – Central overview of system metrics and active security statuses.
2. **Threat Analysis** – Real-time inspection of security events and anomaly detection.
3. **Threat Intelligence** – Structured repository of known threat indicators and patterns.
4. **Expert System** – Rule-based inference engine for automated threat evaluation and mitigation recommendations.
5. **AI Prediction** – Machine learning classification powered by a Random Forest model.
6. **System Workflow** – Visual representation of the end-to-end threat analysis pipeline.
7. **Security Reports** – Automated generation of detailed incident and analysis reports.
8. **Voice Assistant** – Hands-free voice interaction for querying threat statuses and insights.

#### Tech Stack
* **Language:** Python
* **Framework:** Streamlit
* **Machine Learning & Data:** Scikit-learn (Random Forest), Pandas, NumPy
* **Visualization:** Plotly
* **Architecture:** Rule-Based Expert System + Supervised ML

#### Project Structure
```text
CyberGuard_AI/
├── .streamlit/          # Streamlit theme and server configuration
├── assets/              # Project logos and visual assets
├── cyberguard/          # Core modules and voice assistant logic
├── data/                # Sample security events dataset (CSV)
├── models/              # Trained threat classification model (.pkl)
├── pages/               # Multi-page Streamlit UI modules
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
└── streamlit_app.py     # Main application entry point

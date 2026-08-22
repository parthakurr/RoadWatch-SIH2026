# RoadWatch — 3-Developer Multi-Device Collaboration Guide (GitHub Workflow)

This guide provides step-by-step instructions for setting up GitHub so all 3 team members can work simultaneously from their own laptops/devices without code conflicts or breaking each other's work.

---

## 🐙 Step 1: Initialize Local Git Repository & Push to GitHub

Run these commands on the primary device to upload the code to GitHub:

```bash
cd /Users/parththakur/.gemini/antigravity/scratch/roadwatch

# 1. Initialize Git & commit initial codebase
git init
git add .
git commit -m "feat: initial RoadWatch SIH codebase (Edge, Backend, Frontend, Training, Docs)"
git branch -M main

# 2. Link to your GitHub Repository (Create a new private/public repo on GitHub.com first)
git remote add origin https://github.com/YOUR_USERNAME/RoadWatch-SIH2026.git
git push -u origin main
```

---

## 👥 Step 2: Invite Teammates on GitHub
1. Open your repo on GitHub: `https://github.com/YOUR_USERNAME/RoadWatch-SIH2026`
2. Go to **Settings -> Collaborators -> Add people**.
3. Add the GitHub usernames or emails of your 2 teammates.

---

## 💻 Step 3: Teammate Device Setup (Clone & Run Locally)

Each teammate clones the repository to their own computer (Mac, Windows, or Linux):

```bash
git clone https://github.com/YOUR_USERNAME/RoadWatch-SIH2026.git
cd RoadWatch-SIH2026
```

---

## 🌿 Step 4: Branching Strategy (Zero Merge Conflicts)

To ensure nobody overwrites anyone else's code, each teammate works on their assigned feature branch:

| Teammate | Assigned Subsystem | Working Branch Name | Switch Command |
| :--- | :--- | :--- | :--- |
| **Teammate 1** | Raspberry Pi & Edge Daemon | `feature/edge-daemon` | `git checkout -b feature/edge-daemon` |
| **Teammate 2** | AI Model & Colab Training | `feature/ai-model` | `git checkout -b feature/ai-model` |
| **Teammate 3** | FastAPI & React GIS Map | `feature/fullstack-app` | `git checkout -b feature/fullstack-app` |

### Daily Git Routine for Each Teammate:
```bash
# Before starting work (get latest changes from main branch)
git checkout main
git pull origin main
git checkout feature/YOUR-BRANCH-NAME
git merge main

# Do your work, write code...

# Save and push your progress to GitHub
git add .
git commit -m "feat: added new feature details"
git push origin feature/YOUR-BRANCH-NAME
```

---

## 🛠️ How Each Teammate Runs the Code Independently on Their Own Laptop

### 👤 Teammate 1 (Edge & Hardware Lead):
Can run and test the edge daemon locally on any laptop using simulated camera & GPS:
```bash
cd edge
python3 main.py --mock --backend-url http://localhost:8000
```

### 👤 Teammate 2 (AI Training Lead):
Works in Google Colab using the notebook/instructions in `ai_training/README.md`. When new model weights are exported, they simply commit the labels/config or share the model `.tflite` file via Google Drive / GitHub Releases.

### 👤 Teammate 3 (Full-Stack & Dashboard Lead):
Runs backend and frontend locally:
```bash
# Terminal 1: Backend API
cd backend
python3 seed_sqlite.py
python3 app/main.py

# Terminal 2: React Dashboard
cd frontend
npm install
npm run dev
```

---

## 🤝 Step 5: Merging Code Before Demo / Pitch
When a feature is tested and ready, open a **Pull Request (PR)** on GitHub to merge `feature/YOUR-BRANCH` into `main`. Once approved, everyone pulls the updated `main` branch!

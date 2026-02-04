# PhishDetect

A Hybrid URL-DOM Based Phishing Detection Framework with machine learning, DOM analysis, and visual similarity detection.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![Node.js](https://img.shields.io/badge/Node.js-18+-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## Overview

PhishDetect uses a multi-layered approach to detect phishing websites:

1. **URL Analysis** - ML model analyzes URL patterns and characteristics
2. **DOM Analysis** - Compares page structure with legitimate brand templates using Tree Edit Distance
3. **Visual Analysis** - Uses SSIM (Structural Similarity Index) to detect visual clones
4. **Fusion Scoring** - Combines all signals for final prediction

## Project Structure

```
main-project/
├── backend/              # FastAPI Python backend
│   ├── app/              # Application code
│   │   ├── api/          # API routes
│   │   ├── core/         # DOM & Visual analysis modules
│   │   └── ml/           # ML prediction
│   ├── scripts/          # Puppeteer scripts for DOM extraction
│   ├── requirements.txt  # Python dependencies
│   ├── package.json      # Node.js dependencies (Puppeteer)
│   └── Dockerfile
├── frontend/             # Web interface
│   └── src/              # HTML, CSS, JS
├── models/               # Pre-trained ML models
│   ├── url_model/        # URL prediction model (.keras)
│   └── fusion/           # Fusion scoring parameters
├── docs/                 # Documentation
└── docker-compose.yml
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 8+ | `npm --version` |

---

### Option 1: Run Locally (Recommended for Development)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/royalkuriyakosem/main-project.git
cd main-project
```

#### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (required for DOM & Visual analysis)
npm install
```

#### Step 4: Run the Application

```bash
# Start the server (from backend directory)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 5: Access the Application

Open your browser and navigate to: **http://localhost:8000**

---

### Option 2: Run with Docker

```bash
# Build and run containers
docker-compose up --build

# Access the app
open http://localhost:8000

# Stop containers
docker-compose down
```

---

## 📖 API Usage

### Analyze a URL

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "brand": ""}'
```

### Response Example

```json
{
  "url": "https://facebook.com",
  "brand": "facebook",
  "domain_match": true,
  "url_score": 0.007,
  "dom_score": 1.0,
  "visual_score": 1.0,
  "similarity_score": 1.0,
  "hybrid_score": 0.901,
  "threshold": 0.5,
  "final_label": "Legitimate"
}
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| DOM & Visual scores are 0.0 | Run `npm install` in the `backend/` directory |
| CUDA warnings | Safe to ignore - TensorFlow will use CPU |
| scikit-learn version warning | Models work but consider retraining with newer version |
| Port 8000 already in use | Use `--port 8001` or kill the existing process |

---

## 📚 Documentation

- [Architecture & Flow](docs/architecture_and_flow.md)
- [Project Overview](docs/project_overview.md)
- [Run Instructions](docs/run_instructions.md)
- [Innovation Roadmap](docs/innovation_roadmap.md)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.12 |
| ML | TensorFlow, scikit-learn |
| DOM Extraction | Puppeteer, Node.js |
| Visual Analysis | OpenCV, scikit-image (SSIM) |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Containerization | Docker, Docker Compose |

---

## 📝 License

MIT License

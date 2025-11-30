# 📚 BookFinder AI

> **An intelligent, semantic book recommendation engine powered by generic AI and Vector Search.**

![Project Status](https://img.shields.io/badge/Status-MVP-success) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Stack](https://img.shields.io/badge/Stack-FastAPI_|_React_|_Streamlit-orange) ![License](https://img.shields.io/badge/License-MIT-green)

## 📖 Project Overview
**BookFinder AI** goes beyond simple keyword matching. It uses **Natural Language Processing (NLP)** and **Vector Embeddings** to understand the *meaning* and *vibe* of your search query. Whether you're looking for "a sci-fi mystery with time travel" or "a heartbreaking story about friendship in the 1920s," BookFinder AI understands the context and retrieves the most semantically similar books from a dataset of 100,000+ titles.

## 🚩 Problem Statement
Traditional book recommendation systems often rely on:
1.  **Collaborative Filtering:** "Users who bought X also bought Y" (requires massive user data, suffers from "cold start").
2.  **Keyword Matching:** Fails to capture nuance (e.g., searching for "coming of age" might miss books that describe "growing up" without using that exact phrase).

**The Solution:** A **Content-Based Semantic Search** engine that maps books and user queries into a shared high-dimensional vector space, allowing for nuanced, meaning-based discovery.

## 🏗️ Solution Architecture

The system follows a modern **Hybrid Architecture**:

### 1. The Brain (ML Pipeline)
*   **Embeddings:** uses `sentence-transformers/all-MiniLM-L6-v2` to convert book descriptions into 384-dimensional vectors.
*   **Vector Search:** uses **FAISS (Facebook AI Similarity Search)** for ultra-fast similarity retrieval.
*   **Clustering:** uses **K-Means** to automatically group books into thematic collections (e.g., "Space Opera", "Regency Romance").
*   **Explainability:** Uses **Groq (Llama 3)** to generate human-readable explanations for *why* a book was recommended.

### 2. The Backend (API)
*   **Framework:** FastAPI (Python).
*   **Features:** Async endpoints, caching (LRU + Disk), Rate Limiting.
*   **Deployment:** Dockerized, self-healing (auto-downloads data from Hugging Face).

### 3. The Frontend (UI)
*   **Primary:** React (Vite + Tailwind CSS + TypeScript) - A modern, responsive web app.
*   **Admin/Prototyping:** Streamlit - A dashboard for testing and analytics.

---

## ✨ Key Features
*   **Semantic Search:** Query in natural language (e.g., "books like Harry Potter but darker").
*   **Hybrid Recommendations:** Combine semantic similarity with filters (rating, genre).
*   **AI Explanations:** "You got this recommendation because..." (Personalized insights).
*   **Automatic Clustering:** Browse auto-generated "collections" of books.
*   **Feedback Loop:** Users can rate recommendations to help improve the system (logged for analytics).

---

## 🚀 Setup Instructions

### Prerequisites
*   Python 3.10+
*   Node.js 18+ (for Frontend)
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/bookfinder-ai.git
cd bookfinder-ai
```

### 2. Backend Setup
It is recommended to use a virtual environment.

```bash
# Install uv (fast pip replacement) - Optional but recommended
pip install uv

# Create and activate venv
uv venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Data Preparation (The "Magic" Step)
You have two options: **Download Pre-computed Data** (Fast) or **Generate from Scratch** (Slow).

**Option A: Download (Recommended)**
The app includes a script to pull processed data (embeddings, clusters) from Hugging Face.
```bash
python scripts/download_data.py
```

**Option B: Generate from Scratch**
If you want to process the raw CSV yourself (takes ~2-3 hours on CPU):
```bash
# 1. Clean and Prepare Raw Data
python scripts/prepare_100k_data.py
python src/book_recommender/data/processor.py

# 2. Generate Embeddings (The heavy lifting)
python src/book_recommender/ml/embedder.py

# 3. Pre-compute Clusters
python scripts/precompute_clusters.py
```

### 4. Run the Application

**Start the Backend API:**
```bash
python src/book_recommender/api/main.py
# API will run at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Start the React Frontend:**
```bash
cd frontend
npm install
npm run dev
# UI will run at http://localhost:5173
```

**(Optional) Run the Streamlit Dashboard:**
```bash
streamlit run src/book_recommender/apps/main_app.py
```

---

## 🐳 Docker Deployment

The project is fully Dockerized.

```bash
# Build and Run Backend
docker build -t bookfinder-api -f docker/Dockerfile.backend .
docker run -p 8000:8000 bookfinder-api
```

*Note: The Docker container automatically runs `scripts/download_data.py` on startup to fetch the latest data artifacts.*

---

## 🧪 Usage Examples

**API Request (Recommendation):**
```bash
curl -X POST "http://localhost:8000/recommend/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "cyberpunk detective in neo-tokyo", "top_k": 5}'
```

**API Request (Explainability):**
```bash
curl -X POST "http://localhost:8000/explain" \
     -d '{"query_text": "...", "recommended_book": {...}, "similarity_score": 0.85}'
```

---

## 🤝 Contributing
Contributions are welcome!
1.  Fork the repo.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
````markdown
# 🎥 Face-Search Video Demo
A real-time face search system that matches webcam frames or uploaded images against a database of 1,000 faces using **FastAPI**, **FaceNet**, **FAISS**, and **Socket.IO** — containerized with Docker, deployed on **Cloud Run**, and served through **Firebase Hosting**.

## 🔍 Features
- 🔁 Real-time video search using WebSockets at ~10 FPS  
- 📸 Single-image face search via HTTP `POST /search/`  
- 🧠 Face detection with MTCNN and embedding via FaceNet (InceptionResnetV1)  
- ⚡ Similarity search using FAISS IndexFlatL2 returning top 5 matches  
- ☁️ Deployed on Google Cloud Run with Docker and Artifact Registry  
- 🌐 Frontend hosted on Firebase with rewrites to backend API  

## 🏗 Architecture
```
Browser (Webcam + JS UI)
 │
 ├── HTTP /search/        → FastAPI on Cloud Run
 └── WebSocket /socket.io/ → Socket.IO on Cloud Run
All static assets served from Firebase Hosting
```

## 📋 Prerequisites
- Python 3.12+  
- Google Cloud SDK (`gcloud`)  
- Firebase CLI (`firebase-tools`)  
- Docker  
- Node.js & npm  
- Git  

## ⚙️ Local Development

### 1. Clone and Set Up
```bash
git clone https://github.com/<your-username>/face-search.git
cd face-search-video-demo
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate FAISS Index
```bash
python build_index.py
```

### 3. Run Backend API
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Serve Frontend
```bash
cd public
python -m http.server 5000
```

Visit http://localhost:5000/index.html and allow camera access.

## 🐳 Docker & Cloud Run Deployment

### 1. Build and Push Docker Image
```bash
docker build -t us-central1-docker.pkg.dev/$GCP_PROJECT/face-search:latest .
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/$GCP_PROJECT/face-search:latest
```

### 2. Deploy to Cloud Run (PowerShell-friendly)
```powershell
gcloud run deploy face-search-api `
  --image=us-central1-docker.pkg.dev/$GCP_PROJECT/face-search:latest `
  --platform=managed `
  --region=us-central1 `
  --allow-unauthenticated `
  --concurrency=1 `
  --memory=1Gi `
  --timeout=60s
```

After deployment, your service URL will look like:  
`https://face-search-api-xxxxx-uc.a.run.app`

## 🌐 Firebase Hosting Setup

### 1. Initialize Firebase Hosting
```bash
firebase login
firebase init hosting
```
- Use an existing project (e.g. `face-search-12345`)
- Set `public` as the hosting directory
- Decline overwriting `index.html`
- Skip GitHub deploy setup (optional)

### 2. Edit `firebase.json` for Cloud Run rewrites
```json
{
  "hosting": {
    "public": "public",
    "rewrites": [
      { "source": "/search/**",      "run": { "serviceId": "face-search-api", "region": "us-central1" } },
      { "source": "/socket.io",      "run": { "serviceId": "face-search-api", "region": "us-central1" } },
      { "source": "/socket.io/**",   "run": { "serviceId": "face-search-api", "region": "us-central1" } },
      { "source": "**",              "destination": "/index.html" }
    ]
  }
}
```

### 3. Deploy to Firebase Hosting
```bash
firebase deploy --only hosting
```

App will be available at:  
`https://face-search-12345.web.app`

## 🚀 Usage

### 🔸 Single-Image Search via HTTP
```bash
curl -F 'file=@face.jpg' https://face-search-12345.web.app/search/
```

### 🔸 Real-Time Video Search
Open your Firebase Hosting URL, allow camera access, and watch the top 5 matches update live.

## 📂 Project Structure
```
.
├── raw_faces/           # Original face images
├── cropped_faces/       # Cropped face images (MTCNN)
├── build_index.py       # FAISS index builder
├── main.py              # FastAPI + Socket.IO backend
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
├── firebase.json        # Firebase Hosting config
├── public/              # Static frontend (index.html, JS, CSS)
├── faces.index          # FAISS binary index file
└── paths.npy            # Numpy array of image paths
```

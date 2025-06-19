🎥 Face-Search Video Demo
A real-time face search system that matches webcam frames or uploaded images against a database of 1,000 faces using FastAPI, FaceNet, FAISS, and Socket.IO—containerized with Docker, deployed via Cloud Run, and served through Firebase Hosting.

🔍 Features
🔁 Real-time video search using WebSockets at ~10 FPS

📸 Single-image face search via HTTP POST /search/

🧠 Face detection using MTCNN, embeddings with FaceNet (InceptionResnetV1)

⚡ Fast similarity search using FAISS IndexFlatL2 (top 5 matches)

☁️ Cloud-native deployment with Docker → Artifact Registry → Cloud Run

🌐 Frontend hosted on Firebase with rewrite rules to Cloud Run backend

🏗 Architecture
plaintext
Copy
Edit
Browser (JS + Webcam UI)
 │
 ├── HTTP /search/         → FastAPI (Cloud Run)
 └── WebSocket /socket.io/ → Socket.IO (Cloud Run)
 
All assets hosted on Firebase Hosting
📋 Prerequisites
Python 3.12+

Google Cloud SDK

Firebase CLI

Docker

Node.js & npm

Git

⚙️ Local Development
1. Clone and Set Up
bash
Copy
Edit
git clone https://github.com/<your-username>/face-search-video-demo.git
cd face-search-video-demo
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
2. Generate FAISS Index
bash
Copy
Edit
python build_index.py
3. Run Backend API
bash
Copy
Edit
uvicorn main:app --reload --host 0.0.0.0 --port 8000
4. Serve Frontend
bash
Copy
Edit
cd public
python -m http.server 5000
Visit http://localhost:5000/index.html and allow webcam access.

🐳 Docker & Cloud Run Deployment
1. Build and Push Docker Image
bash
Copy
Edit
docker build -t us-central1-docker.pkg.dev/$GCP_PROJECT/face-search:latest .
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/$GCP_PROJECT/face-search:latest
2. Deploy to Cloud Run
bash
Copy
Edit
gcloud run deploy face-search-api `
  --image=us-central1-docker.pkg.dev/$GCP_PROJECT/face-search:latest `
  --platform=managed `
  --region=us-central1 `
  --allow-unauthenticated `
  --concurrency=1 `
  --memory=1Gi `
  --timeout=60s
After deployment, note your service URL, e.g.:
https://face-search-api-xxxxxx-uc.a.run.app

🌐 Firebase Hosting Setup
1. Initialize Firebase
bash
Copy
Edit
firebase login
firebase init hosting
Choose: Use an existing project

Select: face-search-12345

Set public as the hosting directory

Decline overwriting index.html

Skip GitHub deploys if not needed

2. Update firebase.json with Cloud Run rewrites
json
Copy
Edit
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
3. Deploy
bash
Copy
Edit
firebase deploy --only hosting
Your demo will be live at:
https://face-search-12345.web.app

🚀 Usage
🔸 Single-image Search (via HTTP)
bash
Copy
Edit
curl -F 'file=@face.jpg' https://face-search-12345.web.app/search/
🔸 Real-time Search (via browser)
Go to your deployed URL and allow camera access. You’ll see live updates with the top 5 matches.

📂 Project Structure
plaintext
Copy
Edit
.
├── raw_faces/           # Original face images
├── cropped_faces/       # Cropped output from MTCNN
├── build_index.py       # Script to build FAISS index
├── main.py              # FastAPI + Socket.IO backend
├── requirements.txt
├── Dockerfile
├── firebase.json
├── public/              # Frontend UI (HTML, JS, CSS)
├── faces.index          # FAISS binary index file
└── paths.npy            # Numpy array of image paths
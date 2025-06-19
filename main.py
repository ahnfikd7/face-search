import io
import cv2
import numpy as np
import torch
import faiss
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import socketio
from socketio import ASGIApp
from facenet_pytorch import MTCNN, InceptionResnetV1


# ensure index files exist
assert os.path.exists("faces.index"), "Missing faces.index!"
assert os.path.exists("paths.npy"), "Missing paths.npy!"

# initialize face detector and embedder
detector = MTCNN(image_size=160, margin=0)
embedder = InceptionResnetV1(pretrained='vggface2').eval()

# load FAISS index and paths
idx = faiss.read_index("faces.index")
paths = np.load("paths.npy", allow_pickle=True)

def detect_and_search_image(img: np.ndarray) -> list:
    """
    Detects a face in the given BGR OpenCV image, computes embedding,
    searches FAISS for top-5 matches, and returns their file paths.
    """
    face = detector(img)
    if face is None:
        return []
    emb = embedder(face.unsqueeze(0)).detach().numpy()
    D, I = idx.search(emb, k=5)
    return [paths[i] for i in I[0].tolist()]

# initialize Socket.IO server for real-time
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# initialize FastAPI app
app = FastAPI()
# add CORS middleware to allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount Socket.IO ASGI app at root
app.mount("/socket.io", ASGIApp(sio), name="socketio")

# HTTP endpoint for single-image search
@app.post("/search/")
async def search(file: UploadFile = File(...)):
    data = await file.read()
    npimg = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    matches = detect_and_search_image(img)
    return {"matches": matches}

# WebSocket handler for streaming frames
@sio.on("frame")
async def handle_frame(sid, data):
    # data is the raw JPEG bytes from client
    npimg = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    matches = detect_and_search_image(img)
    # emit matches back to this client
    await sio.emit("matches", {"matches": matches}, to=sid)

if __name__ == "__main__":
    pass
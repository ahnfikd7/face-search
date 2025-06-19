# build_index.py
import numpy as np
import faiss
from facenet_pytorch import InceptionResnetV1
import cv2, os

import torch

# load model
model = InceptionResnetV1(pretrained='vggface2').eval()

# load & preprocess
def preprocess(path):
  img = cv2.imread(path)
  img = cv2.resize(img, (160,160))
  img = img[:, :, ::-1]  # BGR→RGB
  return (img / 255.).transpose(2,0,1)[None]

embeddings = []
paths = []
for fn in os.listdir("cropped_faces"):
  arr = preprocess(f"cropped_faces/{fn}")
  emb = model(torch.tensor(arr).float()).detach().numpy()
  embeddings.append(emb.squeeze())
  paths.append(f"cropped_faces/{fn}")

X = np.stack(embeddings)
# build FAISS index
dim = X.shape[1]
idx = faiss.IndexFlatL2(dim)
idx.add(X)
faiss.write_index(idx, "faces.index")
np.save("paths.npy", paths)

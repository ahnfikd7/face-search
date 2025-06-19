# crop_faces.py
from mtcnn import MTCNN
import cv2, os
detector = MTCNN()
os.makedirs("cropped_faces", exist_ok=True)

for fn in os.listdir("raw_faces"):
  img = cv2.imread(f"raw_faces/{fn}")
  res = detector.detect_faces(img)
  if not res: continue
  x, y, w, h = res[0]['box']
  face = img[y:y+h, x:x+w]
  cv2.imwrite(f"cropped_faces/{fn}", face)

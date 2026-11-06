import os
import cv2
import numpy as np
import pytesseract
from dotenv import load_dotenv

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

WHITELIST = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def preprocess(img):
    arr = np.array(img.convert("L"))
    arr = cv2.resize(arr, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    arr = cv2.medianBlur(arr, 3)
    _, arr = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return arr

def solve(img):
    cfg = f"--psm 8 --oem 3 -c tessedit_char_whitelist={WHITELIST}"
    data = pytesseract.image_to_data(
        preprocess(img), config=cfg, output_type=pytesseract.Output.DICT)
    parts = [(t.strip(), float(c)) for t, c in zip(data["text"], data["conf"])
             if t.strip() and float(c) >= 0]
    if not parts:
        return {"text": "", "confidence": 0.0}
    return {"text": "".join(t for t, _ in parts),
            "confidence": round(sum(c for _, c in parts) / len(parts), 1)}
import random
from PIL import Image, ImageDraw, ImageFont

CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_text(length=5):
    text = "".join(random.choices(CHARS, k=length))
    w, h = 60 * length + 20, 90
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except OSError:
        font = ImageFont.load_default()
    for i, ch in enumerate(text):
        g = random.randint(0, 90)
        d.text((15 + i * 55, random.randint(8, 25)), ch, fill=(g, g, g), font=font)
    for _ in range(4):
        d.line([(random.randint(0, w), random.randint(0, h)),
                (random.randint(0, w), random.randint(0, h))],
               fill=(150, 150, 150), width=1)
    return text, img
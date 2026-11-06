def detect_provider(html: str):
    h = html.lower()
    if "g-recaptcha" in h or "google.com/recaptcha" in h:
        return "recaptcha"
    if "h-captcha" in h or "hcaptcha.com" in h:
        return "hcaptcha"
    if "cf-turnstile" in h or "challenges.cloudflare.com/turnstile" in h:
        return "turnstile"
    return None

def detect_image_challenge(img):
    w, h = img.size
    if w < 60 or h < 20 or w > 4000 or h > 2000:
        return "unsupported"
    ratio = w / h
    return "text_image" if 1.5 <= ratio <= 8 else "unsupported"
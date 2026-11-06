import base64
import io
import json
import time

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from PIL import Image

from .models import Challenge
from .services import detector, generator, solver, stats, verifier

def _b64(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()

def run_solve(img, truth=None):
    start = time.perf_counter()
    kind = detector.detect_image_challenge(img)
    if kind == "unsupported":
        stats.record(kind, "none", False, 0, "unsupported_type")
        return {"status": "unsupported", "challenge_type": kind}
    try:
        res = solver.solve(img)
    except Exception as e:
        stats.record(kind, "tesseract_ocr", False, 0, "solver_error")
        return {"status": "error", "challenge_type": kind, "detail": type(e).__name__}
    ms = (time.perf_counter() - start) * 1000
    ok = (res["text"] == truth) if truth is not None else res["confidence"] >= 60
    stats.record(kind, "tesseract_ocr", ok, ms, "" if ok else "wrong_or_low_confidence")
    return {"status": "solved", "challenge_type": kind, "method": "tesseract_ocr",
            "answer": res["text"], "confidence": res["confidence"],
            "correct": ok if truth is not None else None, "time_ms": round(ms, 1)}

@require_GET
def index(request):
    keys = verifier.SITEKEYS()

    return render(request, "index.html", {"keys": keys})

@require_POST
def generate(request):
    text, img = generator.generate_text()
    png = _b64(img)
    c = Challenge.objects.create(answer=text, image_png=png)
    return JsonResponse({"id": str(c.id), "image": base64.b64encode(png).decode()})

@require_POST
def solve(request):
    if "file" in request.FILES:
        try:
            img = Image.open(request.FILES["file"])
            img.load()
        except Exception:
            return JsonResponse({"status": "error", "detail": "invalid_image"}, status=400)
        return JsonResponse(run_solve(img))
    try:
        c = Challenge.objects.get(pk=request.POST.get("id", ""))
    except (Challenge.DoesNotExist, ValueError, Exception):
        return JsonResponse({"status": "error", "detail": "no_challenge"}, status=400)
    img = Image.open(io.BytesIO(bytes(c.image_png)))
    return JsonResponse(run_solve(img, c.answer))

@require_POST
def batch(request):
    try:
        n = min(int(json.loads(request.body or "{}").get("n", 20)), 200)
    except (ValueError, TypeError):
        n = 20
    correct = 0
    for _ in range(n):
        text, img = generator.generate_text()
        correct += bool(run_solve(img, text).get("correct"))
    return JsonResponse({"batch_size": n, "correct": correct,
                         "accuracy": round(100 * correct / n, 1)})

@require_POST
def detect(request):
    html = json.loads(request.body or "{}").get("html", "")
    return JsonResponse({"provider": detector.detect_provider(html) or "unsupported"})

@require_POST
def verify(request):
    try:
        d = json.loads(request.body or "{}")
    except ValueError:
        d = {}
    res = verifier.verify(d.get("provider", ""), d.get("token", ""))
    stats.record(res["provider"], "official_verify", res["success"],
                 res["time_ms"], res["reason"])
    return JsonResponse(res)

@require_GET
def get_stats(request):
    
    return JsonResponse(stats.summary())
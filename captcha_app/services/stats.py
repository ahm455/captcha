from django.db.models import Avg, Count, Q, Sum
from captcha_app.models import AttemptLog

COST = {"tesseract_ocr": 0, "official_verify": 0}

def record(challenge_type, method, success, time_ms, reason=""):
    AttemptLog.objects.create(
        challenge_type=challenge_type, method=method, success=success,
        time_ms=time_ms, reason=reason, cost_usd=COST.get(method, 0))

def summary():
    a = AttemptLog.objects.aggregate(
        total=Count("id"), ok=Count("id", filter=Q(success=True)),
        avg=Avg("time_ms"), cost=Sum("cost_usd"))
    total, ok = a["total"] or 0, a["ok"] or 0
    recent = [{"type": r.challenge_type, "method": r.method, "success": r.success,
               "reason": r.reason, "time_ms": round(r.time_ms, 1),
               "at": r.created_at.strftime("%H:%M:%S")}
              for r in AttemptLog.objects.order_by("-id")[:10]]
    return {"total": total, "successful": ok, "failed": total - ok,
            "success_rate": round(100 * ok / total, 1) if total else 0,
            "avg_time_ms": round(a["avg"] or 0, 1),
            "total_cost_usd": float(a["cost"] or 0),
            "recent": recent}
import hashlib
import os
import time

import requests

from captcha_app.models import UsedToken

ENDPOINTS = {
    "recaptcha": "https://www.google.com/recaptcha/api/siteverify",
    "hcaptcha": "https://api.hcaptcha.com/siteverify",
    "turnstile": "https://challenges.cloudflare.com/turnstile/v0/siteverify",
}

REQUEST_TIMEOUT = 8  # seconds


def _secret(provider):
    """Secrets are read from the environment at call time and never returned or logged."""
    return {
        "recaptcha": os.getenv("RECAPTCHA_SECRET"),
        "hcaptcha": os.getenv("HCAPTCHA_SECRET"),
        "turnstile": os.getenv("TURNSTILE_SECRET_PASS"),
        "turnstile_fail": os.getenv("TURNSTILE_SECRET_FAIL"),
        "turnstile_spent": os.getenv("TURNSTILE_SECRET_SPENT"),
    }.get(provider)


def SITEKEYS():
    return {
        "recaptcha": os.getenv("RECAPTCHA_SITEKEY"),
        "hcaptcha": os.getenv("HCAPTCHA_SITEKEY"),
        "turnstile": os.getenv("TURNSTILE_SITEKEY"),
    }


def _result(provider, ok, reason, start):
    return {
        "provider": provider,
        "success": ok,
        "reason": reason,
        "time_ms": round((time.perf_counter() - start) * 1000, 1),
    }


def verify(provider, token):
    start = time.perf_counter()
    base = (provider or "").split("_")[0]

    # 1. Unsupported provider or missing secret configuration
    if base not in ENDPOINTS or not _secret(provider):
        return _result(provider or "unknown", False, "unsupported_provider", start)

    # 2. Missing token
    if not token or not token.strip():
        return _result(provider, False, "missing_token", start)

    # 3. Local reuse detection (only a SHA-256 fingerprint is stored, never the token)
    fingerprint = hashlib.sha256(token.encode()).hexdigest()
    if UsedToken.objects.filter(fingerprint=fingerprint).exists():
        return _result(provider, False, "reused_token", start)

    # 4. Server-side verification with the provider
    try:
        response = requests.post(
            ENDPOINTS[base],
            data={"secret": _secret(provider), "response": token},
            timeout=REQUEST_TIMEOUT,
        )
        body = response.json()
    except requests.Timeout:
        return _result(provider, False, "provider_timeout", start)
    except (requests.RequestException, ValueError):
        return _result(provider, False, "provider_unreachable", start)

    # 5. Success: remember the token so it cannot be replayed
    if body.get("success"):
        UsedToken.objects.get_or_create(
            fingerprint=fingerprint, defaults={"provider": base}
        )
        return _result(provider, True, "verified", start)

    # 6. Map provider error codes to readable reasons
    codes = body.get("error-codes", [])
    if "timeout-or-duplicate" in codes:
        reason = "expired_or_already_used"
    elif "invalid-input-response" in codes:
        reason = "invalid_token"
    elif "missing-input-response" in codes:
        reason = "missing_token"
    else:
        reason = "rejected_by_provider"
    return _result(provider, False, reason, start)
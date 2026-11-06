
import hashlib
import time

import requests

from captcha_app.models import UsedToken
from captcha_app.services.config import (
    ENDPOINTS,
    REQUEST_TIMEOUT,
    SUPPORTED_PROVIDERS,
    get_secret,
)


# ---------------------------------------------------------------------
# Provider Error Mapping
# ---------------------------------------------------------------------

ERROR_MAPPING = {
    "timeout-or-duplicate": "expired_or_already_used",
    "invalid-input-response": "invalid_token",
    "missing-input-response": "missing_token",
    "invalid-input-secret": "invalid_secret",
    "missing-input-secret": "missing_secret",
    "invalid-or-already-seen-response": "invalid_or_reused_token",
}


# ---------------------------------------------------------------------
# Result Handler
# ---------------------------------------------------------------------

def _result(
    provider: str,
    success: bool,
    reason: str,
    start: float,
) -> dict:
    """Return a standardized verification response."""

    return {
        "provider": provider,
        "success": success,
        "reason": reason,
        "time_ms": round(
            (time.perf_counter() - start) * 1000,
            1,
        ),
    }


# ---------------------------------------------------------------------
# Token Handler
# ---------------------------------------------------------------------

def _fingerprint(token: str) -> str:
    """Generate a SHA-256 fingerprint of a CAPTCHA token."""

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def _is_token_used(fingerprint: str) -> bool:
    """Check whether a CAPTCHA token has already been registered."""

    return UsedToken.objects.filter(
        fingerprint=fingerprint,
    ).exists()


def _register_token(fingerprint: str, provider: str) -> bool:
    """Register a verified token and prevent duplicate registration."""

    _, created = UsedToken.objects.get_or_create(
        fingerprint=fingerprint,
        defaults={
            "provider": provider,
        },
    )

    return created


# ---------------------------------------------------------------------
# Provider Verification
# ---------------------------------------------------------------------

def _verify_provider(
    provider: str,
    secret: str,
    token: str,
) -> tuple[bool, str]:
    """Send a verification request to the CAPTCHA provider."""

    base = (
        "turnstile"
        if provider.startswith("turnstile")
        else provider
    )

    try:
        response = requests.post(
            ENDPOINTS[base],
            data={
                "secret": secret,
                "response": token,
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    except requests.Timeout:
        return False, "provider_timeout"

    except requests.RequestException:
        return False, "provider_unreachable"

    try:
        body = response.json()

    except ValueError:
        return False, "invalid_provider_response"

    if not isinstance(body, dict):
        return False, "invalid_provider_response"

    if body.get("success") is True:
        return True, "verified"

    codes = body.get("error-codes", [])

    if not isinstance(codes, list):
        return False, "invalid_provider_response"

    reason = next(
        (
            ERROR_MAPPING[code]
            for code in codes
            if isinstance(code, str) and code in ERROR_MAPPING
        ),
        "rejected_by_provider",
    )

    return False, reason


# ---------------------------------------------------------------------
# Main Verification Function
# ---------------------------------------------------------------------

def verify(
    provider: str | None,
    token: str | None,
) -> dict:
    """
    Verify a CAPTCHA token.

    Supported providers:
        - recaptcha
        - hcaptcha
        - turnstile
        - turnstile_fail
        - turnstile_spent
    """

    start = time.perf_counter()

    provider = provider.strip() if isinstance(provider, str) else ""
    token = token.strip() if isinstance(token, str) else ""

    # Validate provider.
    if provider not in SUPPORTED_PROVIDERS:
        return _result(
            provider or "unknown",
            False,
            "unsupported_provider",
            start,
        )

    # Validate provider secret.
    secret = get_secret(provider)

    if not secret:
        return _result(
            provider,
            False,
            "missing_secret_configuration",
            start,
        )

    # Validate CAPTCHA token.
    if not token:
        return _result(
            provider,
            False,
            "missing_token",
            start,
        )

    # Generate token fingerprint.
    fingerprint = _fingerprint(token)

    # Prevent token reuse.
    if _is_token_used(fingerprint):
        return _result(
            provider,
            False,
            "reused_token",
            start,
        )

    # Verify with external provider.
    success, reason = _verify_provider(
        provider,
        secret,
        token,
    )

    if not success:
        return _result(
            provider,
            False,
            reason,
            start,
        )

    # Register successfully verified token.
    try:
        registered = _register_token(
            fingerprint,
            provider,
        )

    except Exception:
        return _result(
            provider,
            False,
            "token_registration_failed",
            start,
        )

    if not registered:
        return _result(
            provider,
            False,
            "reused_token",
            start,
        )

    return _result(
        provider,
        True,
        "verified",
        start,
    )


__all__ = ["verify"]

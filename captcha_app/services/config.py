
import os


# ---------------------------------------------------------------------
# Provider Configuration
# ---------------------------------------------------------------------

ENDPOINTS = {
    "recaptcha": "https://www.google.com/recaptcha/api/siteverify",
    "hcaptcha": "https://api.hcaptcha.com/siteverify",
    "turnstile": "https://challenges.cloudflare.com/turnstile/v0/siteverify",
}

SUPPORTED_PROVIDERS = {
    "recaptcha",
    "hcaptcha",
    "turnstile",
    "turnstile_fail",
    "turnstile_spent",
}

REQUEST_TIMEOUT = 8


# ---------------------------------------------------------------------
# Environment Configuration
# ---------------------------------------------------------------------

SITEKEY_ENV = {
    "recaptcha": "RECAPTCHA_SITEKEY",
    "hcaptcha": "HCAPTCHA_SITEKEY",
    "turnstile": "TURNSTILE_SITEKEY",
}

SECRET_ENV = {
    "recaptcha": "RECAPTCHA_SECRET",
    "hcaptcha": "HCAPTCHA_SECRET",
    "turnstile": "TURNSTILE_SECRET_PASS",
    "turnstile_fail": "TURNSTILE_SECRET_FAIL",
    "turnstile_spent": "TURNSTILE_SECRET_SPENT",
}


# ---------------------------------------------------------------------
# Public Configuration
# ---------------------------------------------------------------------

def SITEKEYS() -> dict[str, str]:
    """Return configured public CAPTCHA site keys."""

    return {
        provider: os.getenv(variable, "").strip()
        for provider, variable in SITEKEY_ENV.items()
    }


# ---------------------------------------------------------------------
# Private Configuration
# ---------------------------------------------------------------------

def get_secret(provider: str) -> str | None:
    """Return the configured secret for a CAPTCHA provider."""

    environment_variable = SECRET_ENV.get(provider)

    if not environment_variable:
        return None

    return os.getenv(environment_variable, "").strip() or None


__all__ = [
    "ENDPOINTS",
    "SUPPORTED_PROVIDERS",
    "REQUEST_TIMEOUT",
    "SITEKEYS",
    "get_secret",
]

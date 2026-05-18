import os
from typing import cast

import stripe


def configure_stripe() -> None:
    """Set the Stripe API key from the environment. Idempotent.

    Callers should `import stripe` themselves and use `stripe.Customer`,
    `stripe.checkout`, etc. directly after calling this once per process /
    request lifecycle. Reads STRIPE_SECRET_KEY at call time (not import
    time) so the app boots in environments where Stripe is not yet
    configured.
    """
    secret = os.environ.get("STRIPE_SECRET_KEY")
    if not secret:
        raise RuntimeError("STRIPE_SECRET_KEY is not set")
    stripe.api_key = secret


def verify_webhook(payload: bytes, signature: str) -> dict:
    """Verify a Stripe webhook signature and return the parsed event.

    Raises stripe.error.SignatureVerificationError if the signature is invalid.
    """
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not set")
    return cast(dict, stripe.Webhook.construct_event(payload, signature, secret))

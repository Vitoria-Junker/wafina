from django.conf import settings
import stripe


def get_stripe_client():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


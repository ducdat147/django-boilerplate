from configurations.settings.base import env


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "APP": {
            "client_id": env.str("SOCIALACCOUNT_PROVIDERS_GOOGLE_CLIENT_ID"),
            "secret": env.str("SOCIALACCOUNT_PROVIDERS_GOOGLE_SECRET"),
            "key": "",
        },
        "EMAIL_AUTHENTICATION": True,
    }
}
SOCIALACCOUNT_FORMS = {
    "disconnect": "allauth.socialaccount.forms.DisconnectForm",
    "signup": "allauth.socialaccount.forms.SignupForm",
}

from django.conf import settings


def ai_settings(request):
    return {'ai_enabled': bool(getattr(settings, 'AI_PROVIDER', ''))}

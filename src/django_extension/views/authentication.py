from rest_framework.authentication import TokenAuthentication, SessionAuthentication

__all__ = [
    'BearerTokenAuthentication',
    'CsrfExemptSessionAuthentication'
]

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """SessionAuthentication subclass that skips CSRF validation."""

    def enforce_csrf(self, request):
        # Skip CSRF check entirely
        return
from rest_framework.authentication import TokenAuthentication

__all__ = [
    'BearerTokenAuthentication'
]

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"

# myapp/middleware/token_auth_middleware.py
from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async


# Helper function to get the user associated with the token
@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner  # Reference to the next ASGI application (typically the consumer)

    async def __call__(self, scope, receive, send):
        # Extract token from query string in URL
        query_string = scope.get('query_string', b'').decode()  # Decode query string
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]  # Extract token if present

        # Authenticate the user based on the token
        if token:
            scope['user'] = await get_user_from_token(token)  # Add user to scope if authenticated
        else:
            scope['user'] = AnonymousUser()  # Assign AnonymousUser if no token provided

        # Call the inner application (usually a consumer) to handle the request
        return await self.inner(scope, receive, send)

import os
# from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import realtime.routing
from realtime.token_auth_middleware import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyanase_api.settings')

"""
ASGI config for cyanase_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "websocket": AuthMiddlewareStack(
    "websocket": TokenAuthMiddleware(
        URLRouter(
            realtime.routing.websocket_urlpatterns
        )
    ),
    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(
    #         URLRouter(
    #             realtime.routing.websocket_urlpatterns
    #         )
    #     )
    # ),
})

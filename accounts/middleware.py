import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from accounts.models import User

class JWTMiddleware(MiddlewareMixin):

    def process_request(self, request):
        anon = AnonymousUser()
        request.user = anon
        request._user = anon
        request.auth = None

        auth = request.headers.get('Authorization', '') or request.META.get('HTTP_AUTHORIZATION', '')
        if not auth or not auth.startswith('Bearer '):
            return None

        token = auth.split(' ', 1)[1].strip()
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'], is_active=True)

            request.user = user
            request._user = user
            request.auth = {"type": "jwt"}
        except Exception:
            request.user = anon
            request._user = anon
            request.auth = None

        return None

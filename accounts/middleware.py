import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from accounts.models import User

class JWTMiddleware(MiddlewareMixin):
    """
    Ищет Authorization: Bearer <token>, валидирует JWT и подставляет request.user.
    ВАЖНО: для DRF также выставляем request._user и request.auth.
    """
    def process_request(self, request):
        anon = AnonymousUser()
        request.user = anon               # ← выставляем сразу
        request._user = anon              # ← DRF читает _request.user
        request.auth = None               # ← как в DRF-авторизаторах

        auth = request.headers.get('Authorization', '') or request.META.get('HTTP_AUTHORIZATION', '')
        if not auth or not auth.startswith('Bearer '):
            return None

        token = auth.split(' ', 1)[1].strip()
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'], is_active=True)

            # --- КЛЮЧЕВОЕ: прокинуть пользователя во все места, где DRF его читает ---
            request.user = user
            request._user = user           # ← вот это критично для DRF
            request.auth = {"type": "jwt"} # ← не обязательно, но полезно для дебага
        except Exception:
            request.user = anon
            request._user = anon
            request.auth = None

        return None

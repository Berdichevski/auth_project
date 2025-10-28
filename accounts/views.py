import datetime
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from accounts.permissions import IsAuthenticatedCustom
from accounts.serializers import RegisterSerializer, ProfileSerializer


class RegisterView(APIView):
    """
    Публичная регистрация:
    POST /api/register/  -> {email, first_name, last_name, password, password2}
    """
    authentication_classes = []   # DRF-аутентификацию не используем (JWT в middleware)
    permission_classes = []       # публичная точка

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response({"email": user.email}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Публичный логин:
    POST /api/login/ -> {token}
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"detail": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # срок жизни токена — 1 час
        payload = {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        # PyJWT v2 возвращает str; если у тебя v1 — оберни token = token.decode("utf-8")
        return Response({"token": token}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Формальный логаут для JWT (клиент забывает токен).
    POST /api/logout/
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        return Response({"detail": "Logged out (discard token client-side)"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    Профиль текущего пользователя (требует Bearer токен):
    GET    /api/profile/
    PUT    /api/profile/
    DELETE /api/profile/   -> soft delete (is_active=False)
    """
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data, status=status.HTTP_200_OK)

    def put(self, request):
        ser = ProfileSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)

    def delete(self, request):
        u = request.user
        u.is_active = False
        u.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


# (опционально) Вспомогательный эндпоинт для отладки, можно закоммитить закомментированным
class WhoAmIView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        u = request.user
        return Response(
            {"id": getattr(u, "id", None), "email": getattr(u, "email", None), "class": u.__class__.__name__},
            status=status.HTTP_200_OK,
        )

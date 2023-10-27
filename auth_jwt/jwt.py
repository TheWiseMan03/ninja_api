from django.shortcuts import get_object_or_404
from django.http import Http404
from datetime import datetime, timedelta
from ninja.security import HttpBearer

from django.conf import settings

from ninja_jwt.tokens import AccessToken, RefreshToken
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from ninja.responses import Response
from ninja_extra import status
from movie_ninja.models import Token


class TokenHandler:
    @staticmethod
    def generate_tokens(user):
        access_token = AccessToken()
        refresh_token = RefreshToken()

        token, created = Token.objects.get_or_create(user=user)
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.access_token_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.NINJA_JWT_ACCESS_TOKEN_EXPIRES
        )
        token.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.NINJA_JWT_REFRESH_TOKEN_EXPIRES
        )
        token.save()

        return token

    @staticmethod
    def refresh_tokens(refresh_token):
        token = get_object_or_404(Token, refresh_token=refresh_token)

        if datetime.now(timezone.utc) > token.refresh_token_expires_at:
            return Response(
                {"detail": "Refresh token expired. Please log in again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        new_access_token = AccessToken()
        token.access_token = new_access_token
        token.access_token_expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.NINJA_JWT_ACCESS_TOKEN_EXPIRES
        )
        token.save()

        return token

    @staticmethod
    def get_user_from_token(token: str):
        try:
            token_obj = get_object_or_404(Token, access_token=token)
            user = token_obj.user
        except Http404:
            return None

        return user


class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        if token:
            user = TokenHandler.get_user_from_token(token)
            if user:
                return user

from ninja import Router
from .schemas import (
    RegistrationSchema,
    UpdateSchema,
    PasswordUpdateSchema,
    UserLoginSchema,
    RefreshTokenSchema,
)
from movie_ninja.models import CustomUser
from ninja.responses import Response
from ninja_extra import status
from django.core.exceptions import ObjectDoesNotExist
from .jwt import AuthBearer, TokenHandler
from django.shortcuts import get_object_or_404
from email_validator import validate_email, EmailNotValidError
from django.contrib.auth import authenticate


auth_router = Router()


@auth_router.post("/register")
def register(request, data: RegistrationSchema):
    error_messages = {
        "username": "Missing username field!",
        "email": "Missing email field!",
        "password": "Missing password field!",
        "short_password": "Password too short!",
        "invalid_email": "Invalid email format!",
        "username_taken": "This username is already taken!",
    }

    fields = ["username", "email", "password"]
    for field in fields:
        if not getattr(data, field):
            return Response(
                {"error": error_messages[field]}, status=status.HTTP_400_BAD_REQUEST
            )

    if len(data.password) < 6:
        return Response(
            {"error": error_messages["short_password"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if CustomUser.objects.filter(username=data.username).exists():
        return Response(
            {"error": error_messages["username_taken"]}, status=status.HTTP_409_CONFLICT
        )

    try:
        validate_email(data.email)
    except EmailNotValidError:
        return Response(
            {"error": error_messages["invalid_email"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    CustomUser.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    return Response(
        {"message": "You have Registered Successfully"}, status=status.HTTP_201_CREATED
    )


@auth_router.post("/login", summary="Endpoint to log user in")
def login(request, payload: UserLoginSchema):
    get_object_or_404(CustomUser, username=payload.username)
    user = authenticate(username=payload.username, password=payload.password)
    if user is None:
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
        )

    token = TokenHandler.generate_tokens(user)

    return {
        "access_token": str(token.access_token),
        "access_token_expires_at": token.access_token_expires_at,
        "refresh_token": str(token.refresh_token),
        "refresh_token_expires_at": token.refresh_token_expires_at,
    }


@auth_router.post("/refresh", summary="Endpoint to refresh Access Token")
def refresh(request, refresh_token_data: RefreshTokenSchema):
    token = TokenHandler.refresh_tokens(refresh_token_data.refresh_token)

    if isinstance(token, Response):
        return token

    return {
        "access_token": str(token.access_token),
        "access_token_expires_at": token.access_token_expires_at,
    }


@auth_router.patch("/profile", auth=AuthBearer())
def update_profile(request, update_data: UpdateSchema):
    user = get_object_or_404(CustomUser, username=request.auth)

    for attr, value in update_data.dict().items():
        if attr == "email" and value is not None:
            try:
                validate_email(value)
            except EmailNotValidError:
                return Response(
                    {"detail": "Invalid email address"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if value is not None:
            setattr(user, attr, value)
    user.save()
    return {"detail": "Profile updated successfully"}


@auth_router.put("/update_password", auth=AuthBearer())
def update_password(request, data: PasswordUpdateSchema):
    try:
        user = get_object_or_404(CustomUser, username=data.username)
        if user.check_password(data.password):
            user.set_password(data.new_password)
            user.save()
            return {"detail": "Password updated successfully"}
        else:
            return Response(
                {"detail": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST
            )
    except ObjectDoesNotExist:
        return Response(
            {"detail": "No such user exists"}, status=status.HTTP_400_BAD_REQUEST
        )


@auth_router.delete("/delete-account", auth=AuthBearer(), response={204: None})
def user_delete(request):
    user = get_object_or_404(CustomUser, username=request.auth)
    user.delete()
    return {"detail": "User has been deleted successfully"}

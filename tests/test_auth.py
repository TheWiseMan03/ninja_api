import pytest
from ninja.testing import TestClient
from auth_jwt.views import auth_router
from ninja_extra import status
from movie_ninja.models import CustomUser
from django.shortcuts import get_object_or_404
from django.http import Http404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, email, password, first_name, last_name, expected_status, expected_error",
    [
        (
            "gigi",
            "a@aaaaa.com",
            "456789",
            "First",
            "Last",
            status.HTTP_201_CREATED,
            None,
        ),
        (
            "",
            "user2@example.com",
            "password2",
            "First2",
            "Last2",
            status.HTTP_400_BAD_REQUEST,
            "Missing username field!",
        ),
        (
            "user3",
            "",
            "password3",
            "First3",
            "Last3",
            status.HTTP_400_BAD_REQUEST,
            "Missing email field!",
        ),
        (
            "user4",
            "user4@example.com",
            "",
            "First4",
            "Last4",
            status.HTTP_400_BAD_REQUEST,
            "Missing password field!",
        ),
        (
            "gigia",
            "aa@aaaaa.com",
            "456789",
            "First",
            "Last",
            status.HTTP_409_CONFLICT,
            "This username is already taken!",
        ),
        (
            "user5",
            "invalid_email",
            "password5",
            "First5",
            "Last5",
            status.HTTP_400_BAD_REQUEST,
            "Invalid email format!",
        ),
        (
            "user6",
            "user6@example.com",
            "short",
            "First6",
            "Last6",
            status.HTTP_400_BAD_REQUEST,
            "Password too short!",
        ),
    ],
)
def test_register(
    setup,
    username,
    email,
    password,
    first_name,
    last_name,
    expected_status,
    expected_error,
):
    client = TestClient(auth_router)
    response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    assert response.status_code == expected_status

    if expected_error:
        assert response.json()["error"] == expected_error


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, password, expected_status, expected_error",
    [
        (
            "gigia",
            "456789",
            status.HTTP_200_OK,
            None,
        ),
        (
            "gigia",
            "wrongpassword",
            status.HTTP_400_BAD_REQUEST,
            "Invalid credentials",
        ),
        (
            "nonexistentuser",
            "456789",
            status.HTTP_404_NOT_FOUND,
            "Not Found",
        ),
    ],
)
def test_login(setup, username, password, expected_status, expected_error):
    client = TestClient(auth_router)
    payload = {"username": username, "password": password}
    response = client.post("/login", json=payload)

    assert response.status_code == expected_status

    if expected_error:
        assert response.json()["detail"] == expected_error


def test_update_profile_unauthorized():
    client = TestClient(auth_router)
    response = client.patch(
        "/profile",
        json={
            "first_name": "NewFirst",
            "last_name": "NewLast",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "update_data, expected_status, expected_detail",
    [
        (
            {"first_name": "NewFirst1", "last_name": "NewLast1"},
            status.HTTP_200_OK,
            "Profile updated successfully",
        ),
        (
            {"email": "invalid email"},
            status.HTTP_400_BAD_REQUEST,
            "Invalid email address",
        ),
    ],
)
def test_update_profile(auth_client, update_data, expected_status, expected_detail):
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token.access_token}"}
    response = client.patch("/profile", json=update_data, headers=headers)
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail

    if expected_status == status.HTTP_200_OK:
        user = get_object_or_404(CustomUser, username="gigia")
        for attr, value in update_data.items():
            assert getattr(user, attr) == value


@pytest.mark.django_db
def test_refresh_token(auth_client):
    client, token = auth_client
    response = client.post("/refresh", json={"refresh_token": str(token.refresh_token)})
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["access_token"] != str(token.access_token)

    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    test_response = client.delete("/delete-account", headers=headers)
    assert test_response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, password, new_password, expected_status, expected_detail",
    [
        (
            "gigia",
            "456789",
            "new_password",
            status.HTTP_200_OK,
            "Password updated successfully",
        ),
        (
            "gigia",
            "incorrect_password",
            "new_password",
            status.HTTP_400_BAD_REQUEST,
            "Incorrect password",
        ),
        (
            "incorrect_username",
            "456789",
            "new_password",
            status.HTTP_404_NOT_FOUND,
            "Not Found",
        ),
    ],
)
def test_update_password(
    auth_client, username, password, new_password, expected_status, expected_detail
):
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token.access_token}"}
    response = client.put(
        "/update_password",
        json={
            "username": username,
            "password": password,
            "new_password": new_password,
        },
        headers=headers,
    )

    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail

    if expected_status == status.HTTP_200_OK:
        user = get_object_or_404(CustomUser, username=username)
        assert user.check_password(new_password)


@pytest.mark.django_db
def test_user_delete(auth_client):
    client, token = auth_client

    headers = {"Authorization": f"Bearer {token.access_token}"}
    response = client.delete("/delete-account", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    with pytest.raises(Http404):
        get_object_or_404(CustomUser, username="gigia")

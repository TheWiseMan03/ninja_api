import pytest, json
from ninja.testing import TestClient
from movie_ninja.views import api_router
from ninja_extra import status
from movie_ninja.schemas import MovieListSchema
import time


client = TestClient(api_router)


@pytest.mark.django_db
def test_list_actors_performance():
    start_time = time.time()
    response = client.get("/actors")
    end_time = time.time()
    response_time = end_time - start_time

    assert response.status_code == status.HTTP_200_OK
    assert response_time < 0.1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name,age,description,image_filename,expected_status",
    [
        (
            f"Actor 1",
            30,
            f"Description for Actor 1",
            "file1.jpg",
            status.HTTP_200_OK,
        ),
        (
            f"Actor 2",
            30,
            f"Description for Actor 2",
            "file1.txt",
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            f"Actor 1",
            -10,
            f"Description for Actor 1",
            "file1.jpg",
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_create_actors(name, age, description, image_filename, expected_status):
    actor_data = {
        "name": name,
        "age": age,
        "description": description,
        "image": image_filename,
    }
    response = client.post("/actors", json=actor_data)

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_get_actor(actor_creation):
    actor_id = actor_creation["id"]

    response = client.get(f"/actors/{actor_id}")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_movies(movie_creation):
    response = client.get("/movies")
    assert response.status_code == 200

    movies = response.json()
    assert len(movies) == 1

    movie_schema = MovieListSchema(**movies[0])
    assert movie_schema.id == movie_creation.id
    assert movie_schema.title == movie_creation.title
    assert movie_schema.tagline == movie_creation.tagline
    assert movie_schema.category == movie_creation.category.name
    assert movie_schema.poster == movie_creation.poster


@pytest.mark.django_db
def test_get_movie(movie_creation):
    response = client.get(f"/movies/{movie_creation.id}")
    assert response.status_code == 200

    movie_data = response.json()
    assert movie_data["id"] == movie_creation.id
    assert movie_data["title"] == movie_creation.title


@pytest.mark.django_db
def test_get_movie_not_found():
    response = client.get("/movies/9999")
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "review, status_code",
    [
        (
            {
                "email": "test@example.com",
                "name": "Test Review",
                "text": "Great movie!",
                "parent": None,
            },
            201,
        ),
        ({"email": "", "name": "", "text": "", "parent": None}, 400),
    ],
)
def test_create_review(review, status_code, movie_creation):
    movie_id = movie_creation.id
    response = client.post(f"/reviews?movie_id={movie_id}", json=review)
    assert response.status_code == status_code


@pytest.mark.django_db
def test_get_movie_reviews(movie_creation, reviews_creation):
    response = client.get(f"/movies/{movie_creation.id}/reviews")

    assert response.status_code == 200

    assert len(response.json()) == len(reviews_creation)

    for review_response, review in zip(response.json(), reviews_creation.values()):
        assert review_response["id"] == review.id
        assert review_response["name"] == review.name
        assert review_response["text"] == review.text


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status_code",
    [
        201,
    ],
)
def test_create_rating(status_code, rating_stars_creation, movie_creation):
    ip = "127.0.0.1"
    data = {"ip": ip, "star_id": rating_stars_creation, "movie_id": movie_creation.id}

    response = client.post(
        "/ratings", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == status_code

from pytest_factoryboy import register
import pytest
from movie_ninja.models import (
    Token,
    Movie,
    Category,
    CustomUser,
    Review,
    RatingStar,
    Rating,
)
from ninja.testing import TestClient
from auth_jwt.views import auth_router
from movie_ninja.views import api_router
from .factories import (
    CustomUserFactory,
    TokenFactory,
    CategoryFactory,
    ActorFactory,
    GenreFactory,
    MovieFactory,
    MovieShotsFactory,
    RatingStarFactory,
    RatingFactory,
    ReviewFactory,
)


register(CustomUserFactory)
register(TokenFactory)
register(CategoryFactory)
register(ActorFactory)
register(GenreFactory)
register(MovieFactory)
register(MovieShotsFactory)
register(RatingStarFactory)
register(RatingFactory)
register(ReviewFactory)


# @pytest.mark.django_db
# @pytest.fixture
# def setup():
#     CustomUser.objects.create_user(
#         username="gigia",
#         email="aa@aaaaa.com",
#         password="456789",
#         first_name="First",
#         last_name="Last",
#     )


# @pytest.mark.django_db
# @pytest.fixture
# def auth_client(setup):
#     client = TestClient(auth_router)
#     response = client.post(
#         "/login",
#         json={
#             "username": "gigia",
#             "password": "456789",
#         },
#     )
#     access_token_str = response.json()["access_token"]
#     token_instance = Token.objects.get(access_token=access_token_str)

#     return client, token_instance


@pytest.fixture
def actor_creation():
    actor_data = {
        "name": "Actor 1",
        "age": 30,
        "description": "Description for Actor 1",
        "image": "file1.jpg",
    }
    client = TestClient(api_router)
    response = client.post("/actors", json=actor_data)
    return response.json()


@pytest.fixture
def movie_creation():
    category = Category.objects.create(name="Test Category")
    movie = Movie.objects.create(
        title="Test Movie",
        tagline="Test Tagline",
        description="Test Description",
        poster="Test Poster",
        year=2023,
        country="Test Country",
        world_premiere="2023-01-01",
        budget=1000000,
        fees_in_usa=500000,
        fess_in_world=500000,
        category=category,
        url="test-movie",
        draft=False,
    )
    return movie


@pytest.fixture
def reviews_creation(movie_creation):
    movie = movie_creation

    reviews = {
        "review1": Review.objects.create(
            email="test1@example.com",
            name="Test Review 1",
            text="Great movie!",
            parent=None,
            movie=movie,
        ),
        "review2": Review.objects.create(
            email="test2@example.com",
            name="Test Review 2",
            text="I enjoyed it!",
            parent=None,
            movie=movie,
        ),
    }

    return reviews


@pytest.fixture
def rating_stars_creation():
    star = RatingStar.objects.create(value="4")
    return star.id

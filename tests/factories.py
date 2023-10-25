import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.utils import timezone
from datetime import timedelta
from movie_ninja.models import (
    CustomUser,
    Token,
    Movie,
    Category,
    Actor,
    Genre,
    MovieShots,
    RatingStar,
    Rating,
    Review,
)


faker = Faker()


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda a: f"{a.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class TokenFactory(DjangoModelFactory):
    class Meta:
        model = Token

    user = factory.SubFactory(CustomUserFactory)
    access_token = faker.pystr_format(
        string_format="????-????-????-????",
        letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    access_token_expires_at = timezone.now() + timedelta(minutes=60)
    refresh_token = faker.pystr_format(
        string_format="????-????-????-????",
        letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    refresh_token_expires_at = timezone.now() + timedelta(days=30)


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"category{n}")
    description = factory.Faker("paragraph")
    url = factory.Sequence(lambda n: f"category-{n}")


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Sequence(lambda n: f"genre{n}")
    description = factory.Faker("paragraph")
    url = factory.Sequence(lambda n: f"genre-{n}")


class MovieFactory(DjangoModelFactory):
    class Meta:
        model = Movie

    title = factory.Faker("sentence")
    tagline = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    poster = factory.django.ImageField(color="blue")
    year = factory.Faker("year")
    country = factory.Faker("country")
    world_premiere = factory.Faker("date_this_decade")
    budget = factory.Faker("random_int", min=10000, max=100000000)
    fees_in_usa = factory.Faker("random_int", min=10000, max=100000000)
    fess_in_world = factory.Faker("random_int", min=10000, max=100000000)
    category = factory.SubFactory(CategoryFactory)
    url = factory.Sequence(lambda n: f"movie-{n}")
    draft = False


class MovieShotsFactory(DjangoModelFactory):
    class Meta:
        model = MovieShots

    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    image = factory.django.ImageField(color="blue")
    movie = factory.SubFactory(MovieFactory)


class RatingStarFactory(DjangoModelFactory):
    class Meta:
        model = RatingStar

    value = factory.Iterator([1, 2, 3, 4, 5])


class RatingFactory(DjangoModelFactory):
    class Meta:
        model = Rating

    ip = factory.Faker("ipv4")
    star = factory.SubFactory(RatingStarFactory)
    movie = factory.SubFactory(MovieFactory)


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    email = factory.Faker("email")
    name = factory.Faker("name")
    text = factory.Faker("paragraph")
    parent = None


class ActorFactory(DjangoModelFactory):
    class Meta:
        model = Actor

    name = factory.Faker("name")
    age = factory.Faker("random_int", min=20, max=70)
    description = factory.Faker("paragraph")
    image = factory.django.ImageField(color="blue")

from ninja import Router, Path, Form
from .models import Actor, Movie, Review, Rating, RatingStar
from .schemas import (
    ActorListSchema,
    ActorDetailSchema,
    ActorCreateSchema,
    MovieDetailSchema,
    MovieListSchema,
    CreateMovieSchema,
    ReviewCreateSchema,
    ReviewResponseSchema,
    ReviewSchema,
    CreateRatingSchema,
)
from typing import List
from django.shortcuts import get_object_or_404
from ninja.responses import Response
from ninja_extra import status
import os


api_router = Router()


@api_router.get(
    "/actors", response=List[ActorListSchema], summary="Get list of all actors"
)
def list_actors(request):
    actors = Actor.objects.all()
    actor_list = [
        {"id": actor.id, "name": actor.name, "image": actor.image.url}
        for actor in actors
    ]
    return actor_list


@api_router.post("/actors", response=ActorListSchema, summary="Create a new actor")
def create_actor(request, actor_in: ActorCreateSchema):
    if (
        actor_in.name == ""
        or actor_in.age < 0
        or actor_in.description == ""
        or actor_in.image == None
    ):
        return Response(
            {"detail": "Invalid input"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    valid_image_formats = [".jpg", ".jpeg", ".png"]
    if os.path.splitext(actor_in.image)[1] not in valid_image_formats:
        return Response(
            {"detail": "Invalid image format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    actor = Actor.objects.create(
        name=actor_in.name,
        age=actor_in.age,
        description=actor_in.description,
        image=actor_in.image,
    )

    return {"id": actor.id, "name": actor.name, "image": actor.image}


@api_router.get(
    "/actors/{actor_id}", response=ActorDetailSchema, summary="Get one actor's details"
)
def get_actor(request, actor_id: int = Path(...)):
    actor = get_object_or_404(Actor, id=actor_id)
    return {
        "id": actor.id,
        "name": actor.name,
        "age": actor.age,
        "description": actor.description,
        "image": actor.image,
    }


@api_router.get(
    "/movies", response=List[MovieListSchema], summary="Get list all movies"
)
def list_movies(request):
    movies = Movie.objects.all()
    movie_list = [
        {
            "id": movie.id,
            "title": movie.title,
            "tagline": movie.tagline,
            "category": movie.category.name if movie.category else "",
            "rating_user": True,
            "middle_star": 0,
            "poster": movie.poster,
        }
        for movie in movies
    ]

    return movie_list


@api_router.get(
    "/movies/{movie_id}", response=MovieDetailSchema, summary="Get details of the movie"
)
def get_movie(request, movie_id: int = Path(...)):
    movie = get_object_or_404(Movie, id=movie_id)

    return {
        "id": movie.id,
        "title": movie.title,
        "tagline": movie.tagline,
        "description": movie.description,
        "poster": movie.poster,
        "year": movie.year,
        "country": movie.country,
        "directors": [director.id for director in movie.directors.all()],
        "actors": [actor.id for actor in movie.actors.all()],
        "genres": [genre.id for genre in movie.genres.all()],
        "world_premiere": movie.world_premiere.strftime("%Y-%m-%d"),
        "budget": movie.budget,
        "fees_in_usa": movie.fees_in_usa,
        "fess_in_world": movie.fess_in_world,
        "category": movie.category.name if movie.category else None,
        "url": movie.url,
        "reviews": [review.id for review in movie.reviews.all()],
    }


@api_router.post(
    "/reviews", summary="Create a new review", response=ReviewResponseSchema
)
def create_review(request, movie_id: int, review: ReviewCreateSchema):
    if not review.email or not review.name or not review.text:
        return Response(
            {"detail": "Email, name, and text must not be empty."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    movie = get_object_or_404(Movie, id=movie_id)
    review = Review(movie=movie, **review.dict())

    review.save()
    return Response(
        {
            "name": review.name,
            "text": review.text,
            "parent": review.parent.id if review.parent else None,
            "movie": review.movie.title,
        },
        status=status.HTTP_201_CREATED,
    )


@api_router.get(
    "/movies/{movie_id}/reviews",
    summary="Get all reviews for a movie",
    response=List[ReviewSchema],
)
def get_movie_reviews(request, movie_id: int):
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = Review.objects.filter(movie=movie)
    review_list = []
    for review in reviews:
        review_dict = {"id": review.id, "name": review.name, "text": review.text}
        if review.children:
            children = []
            for child in review.children.all():
                children.append(
                    {"id": child.id, "name": child.name, "text": child.text}
                )
            review_dict["children"] = children
        review_list.append(review_dict)
    return review_list


@api_router.post(
    "/ratings",
    response={201: CreateRatingSchema},
    summary="Create a rating for a specific movie",
)
def create_rating(request, data: CreateRatingSchema):
    ip = data.ip
    star_id = data.star_id
    movie_id = data.movie_id

    star = get_object_or_404(RatingStar, id=star_id)
    movie = get_object_or_404(Movie, id=movie_id)

    rating = Rating(ip=ip, star=star, movie=movie)
    rating.save()

    return 201, rating

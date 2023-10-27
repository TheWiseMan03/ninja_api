from ninja import Schema
from datetime import date
from typing import Optional, List


class ActorListSchema(Schema):
    id: int
    name: str
    image: str


class ActorCreateSchema(Schema):
    name: str
    age: int
    description: str
    image: str


class ActorDetailSchema(Schema):
    id: int
    name: str
    age: str
    description: str
    image: str


class MovieListSchema(Schema):
    id: int
    title: str
    tagline: str
    category: str
    rating_user: bool
    middle_star: int
    poster: str


class CreateMovieSchema(Schema):
    id: int
    title: str
    tagline: str
    description: str
    poster: str
    year: int
    country: str
    directors: List[int]
    actors: List[int]
    genres: List[int]
    world_premiere: date
    budget: int
    fees_in_usa: int
    fess_in_world: int
    category: int
    url: str
    draft: bool


class ReviewCreateSchema(Schema):
    email: str
    name: str
    text: str
    parent: Optional[int]


class ReviewResponseSchema(Schema):
    name: str
    text: str
    parent: Optional[int]
    movie: str


class ReviewSchema(Schema):
    id: int
    name: str
    text: str
    children: List["ReviewSchema"]


class MovieDetailSchema(Schema):
    id: int
    title: str
    tagline: str
    description: str
    poster: str
    year: int
    country: str
    directors: List[ActorListSchema]
    actors: List[ActorListSchema]
    genres: List[str]
    world_premiere: date
    budget: int
    fees_in_usa: int
    fees_in_world: Optional[int]
    category: Optional[str]
    url: str
    reviews: Optional[List[ReviewSchema]]


class CreateRatingSchema(Schema):
    ip: str
    star_id: int
    movie_id: int

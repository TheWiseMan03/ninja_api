from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from auth_jwt.views import auth_router
from movie_ninja.views import api_router


api = NinjaAPI()
api.add_router('auth/', auth_router, tags=['auth'])
api.add_router('', api_router, tags=['api'])

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, FollowView, FollowListViewSet,
                    RecipeViewSet, TagViewSet)

app_name = 'api'

router_v1 = routers.DefaultRouter()

router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('v1/users/subscriptions/',
         FollowListViewSet.as_view({'get': 'list'})),
    path('v1/users/<int:user_id>/subscribe/', FollowView.as_view()),
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.authtoken')),
]

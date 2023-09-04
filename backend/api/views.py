from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, HttpResponse
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from recipes.models import (Favourite, Follow, Ingredient, Purchase, Recipe,
                            RecipesIngredient, Tag)

from .permissions import (AuthorOrReadOnly, IsAdminIsAuthorOrReadOnly,
                          RoleAdminrOrReadOnly)
from .serializers import (FavouriteSerializer, FollowSerializer,
                          FollowListSerializer, IngredientSerializer,
                          PurchaseSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, TagSerializer)
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API для работы с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (RoleAdminrOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """API для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (RoleAdminrOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """API для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = FavouriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id, },
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if not Favourite.objects.filter(user=request.user,
                                        recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favourite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = PurchaseSerializer(
                data={'user': request.user.id, 'recipe': recipe.id, },
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if not Purchase.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Purchase.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipesIngredient.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('count'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measure = ingredient['ingredient__measurement_unit']
            count = ingredient['ingredient_count']
            shopping_list.append(f'\n{name} - {count} {measure}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_cart.txt"')
        return response


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class FollowListViewSet(ListViewSet):
    """API для работы со списком подписок."""

    serializer_class = FollowListSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class FollowView(APIView):
    """API для модели Подписок."""

    def post(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        serializer = FollowSerializer(
            data={'user': request.user.id, 'following': following.id},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        if not Follow.objects.filter(user=request.user,
                                     following=following).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get(user=request.user.id, following=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

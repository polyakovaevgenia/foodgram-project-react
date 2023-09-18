import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favourite, Follow, Ingredient, Purchase, Recipe,
                            RecipesIngredient, Tag)
from users.models import User


class CustomUserSerializer(UserSerializer):
    """Сериалайзер для модели Юзера."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_subscribed')

    # def get_is_subscribed(self, obj):
    #     user = self.context.get('request').user
    #     if not user.is_authenticated:
    #         return False
#     return Follow.objects.filter(user=user, following__id=obj.id).exists()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Follow.objects.filter(
                    user=request.user, following=obj
                ).exists())


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Тэга."""

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug', 'id', 'recipes')

    # def validate_color(self, data):
    #     color = data.get('color')
    #     validate_color = color.strip('#').upper()
    #     if Tag.objects.filter(color=color).exists():
    #         raise serializers.ValidationError("Этот цвет уже занят.")
    #     Tag.objects.get_or_create(
    #         name=data['name'],
    #         color=validate_color,
    #         slug=data['slug'],
    #     )
    #     return data

    # def validate_color(self, value):
    #     if Tag.objects.filter(color=self.request.color).exists():
    #         raise serializers.ValidationError("Этот цвет уже занят")
    #     return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'id', 'recipes')


class IngredientListSerializer(serializers.ModelSerializer):
    """Сериалайзер для получения информации об ингредиентах."""

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Рецепта."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'text', 'tags', 'cooking_time', 'image',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart', 'id')

    # def get_ingredients(self, obj):
    #     recipe = obj
    #     ingredients = recipe.ingredients.values(
    #         'id',
    #         'name',
    #         'measurement_unit',
    #         amount=F('ingredientinrecipe__amount')
    #     )
    #     return ingredients

    def get_ingredients(self, obj):
        ingredients = RecipesIngredient.objects.filter(recipe=obj)
        return IngredientListSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favourite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Purchase.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания или обновления рецепта."""

    image = Base64ImageField(required=False, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientPostSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'tags', 'cooking_time', 'image',
                  'ingredients', 'id', 'author')

    def validate_cooking_time(self, value):
        cooking_time = value
        if cooking_time >= 1:
            return value
        raise serializers.ValidationError("Время приготовления должно быть"
                                          "больше 1 минуты")

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise serializers.ValidationError("Необходим хотя бы один тэг")
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError("Тэги не должны повторяться")
            tags_list.append(tag)
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise serializers.ValidationError("Необходим хотя бы один"
                                              "ингредиент")
        ingredients_list = []
        for ing in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ing['id'])
            if ingredient in ingredients_list:
                raise serializers.ValidationError("Ингредиенты не должны"
                                                  "повторяться")
            if int(ing['amount']) <= 0:
                raise serializers.ValidationError("Ингредиентов должно быть"
                                                  "больше одного")
            ingredients_list.append(ingredient)
        return value

    def create_ingredients_to_recipe(self, ingredients, recipe):
        RecipesIngredient.objects.bulk_create(
            [RecipesIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create_recipe(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_to_recipe(ingredients=ingredients,
                                          recipe=recipe)
        return recipe

    def update_recipe(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipesIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.create_ingredients_to_recipe(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeSerializer(instance,
                                context={'request': request}).data


# class FollowSerializer(serializers.ModelSerializer):
#     """Сериалайзер для модели Подписок."""

#     class Meta:
#         model = Follow
#         fields = ('user', 'following')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'following')
#             )
#         ]

#     def validate_following(self, value):
#         if self.context['request'].user != value:
#             return value
#         raise serializers.ValidationError("Нельзя подписаться на себя")


class FollowListSerializer(CustomUserSerializer):
    """Сериалайзер для отображения страницы подписок."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    # is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('username', 'email', 'first_name', 'last_name',
                            'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipeFollowSerializer(recipes, many=True,
                                      context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    # def get_is_subscribed(self, obj):
    #     return True

    def validate(self, data):
        following = self.instance
        user = self.context.get('request').user
        if Follow().objects.filter(following=following, user=user).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя"
            )
        if user == following:
            raise serializers.ValidationError(
                "Нельзя подписаться на себя"
            )
        return data


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецепта в подписках, избранном, покупках."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Избранного."""

    class Meta:
        model = Favourite
        fields = ('recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Favourite.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeFollowSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class PurchaseSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Покупок."""

    class Meta:
        model = Purchase
        fields = ('recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Purchase.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeFollowSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериалайзер для создания Юзера."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

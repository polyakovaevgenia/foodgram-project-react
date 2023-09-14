from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель Тэга."""

    name = models.CharField('Название', max_length=200, unique=True)
    color = ColorField('Цвет', format='hex')
    slug = models.SlugField('Путь', unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def clean(self):
        self.color == self.color.upper()

    # def clean(self):
    #     if self.color == self.color.upper():
    #         raise ValidationError("Этот цвет уже занят")
    #     super(Tag, self).clean()

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиента."""

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единицы измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    """Модель Рецепта."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Картинка', upload_to='recipes/')
    text = models.TextField('Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipesIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1,
            message='Нельзя готовить меньше 1 минуты!')]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name} - автор {self.author}'


class RecipesIngredient(models.Model):
    """Модель ингредиента для рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Продукт'
    )
    amount = models. PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            1,
            message='Ингредиентов не может быть меньше одного!')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_subscription')
        ]

    def clean(self):
        if self.user == self.following:
            raise ValidationError("Нельзя подписаться на себя")
        super(Follow, self).clean()

    def __str__(self):
        return f'{self.user} подписался на {self.following}'


class CreatedModel(models.Model):
    """Абстрактная модель."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True


class Favourite(CreatedModel):
    """Модель добавления рецепта в избранное."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favourite_recipe')
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в избранное'


class Purchase(CreatedModel):
    """Модель списка покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Покупки'
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_purchase_recipe')
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в список покупок'

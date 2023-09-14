from django.contrib import admin

from .models import (Favourite, Follow, Ingredient, Purchase, Recipe,
                     RecipesIngredient, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    model = RecipesIngredient
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favourites_count')
    readonly_fields = ('favourites_count',)
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = (IngredientInline,)

    def favourites_count(self, obj):
        return Favourite.objects.filter(recipe=obj).count()


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipesIngredient)
admin.site.register(Follow)
admin.site.register(Favourite)
admin.site.register(Purchase)

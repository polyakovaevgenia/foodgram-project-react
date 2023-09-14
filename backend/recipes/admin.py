from django.contrib import admin
# from django.forms import BaseInlineFormSet, ValidationError

from .models import (Favourite, Follow, Ingredient, Purchase, Recipe,
                     RecipesIngredient, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


# class IngredientInlineFormset(BaseInlineFormSet):

#     def is_valid(self):
#         return (super(IngredientInlineFormset, self)
#                 .is_valid()
#                 and not any([bool(error) for error in self.errors]))

#     def clean(self):
#         count = 0
#         for form in self.forms:
#             try:
#                 if (
#                     form.cleaned_data
#                     and not form.cleaned_data.get('DELETE', False)
#                 ):
#                     count += 1
#             except AttributeError:
#                 pass
#         if count < 1:
#             raise ValidationError("Добавьте тэги и ингредиенты")


class IngredientInline(admin.TabularInline):
    model = RecipesIngredient
    extra = 0


class TagInline(admin.TabularInline):
    model = Tag
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favourites_count')
    readonly_fields = ('favourites_count',)
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = (IngredientInline, TagInline,)

    def favourites_count(self, obj):
        return Favourite.objects.filter(recipe=obj).count()


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipesIngredient)
admin.site.register(Follow)
admin.site.register(Favourite)
admin.site.register(Purchase)

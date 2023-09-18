from django.contrib import admin
# from django.forms import BaseInlineFormSet
# from rest_framework import serializers

from .models import (Favourite, Follow, Ingredient, Purchase, Recipe,
                     RecipesIngredient, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


# class MinValidatedInlineMixIn:
#     validate_min = True

#     def get_formset(self, *args, **kwargs):
#         return super().get_formset(
#             validate_min=self.validate_min,
#             *args,
#             **kwargs)


# class IngredientInline(MinValidatedInlineMixIn, admin.TabularInline):
#     model = RecipesIngredient
#     extra = 1
#     min_num = 1
#     validate_min = True

    # def get_formset(self, request, obj=None, **kwargs):
    #     formset = super().get_formset(request, obj=None, **kwargs)
    #     formset.validate_min = True
    #     return formset
    # get_formset(), request)

# class IngredientInlineFormSet(BaseInlineFormSet):

#     def is_valid(self):
#         return (super(IngredientInlineFormset, self).is_valid()
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
#             raise serializers.ValidationError("В рецепте должны быть"
#                                               "теги и ингредиенты")


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favourites_count')
    readonly_fields = ('favourites_count',)
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    # inlines = (IngredientInline,)
    # formset =

    def favourites_count(self, obj):
        return Favourite.objects.filter(recipe=obj).count()


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipesIngredient)
admin.site.register(Follow)
admin.site.register(Favourite)
admin.site.register(Purchase)

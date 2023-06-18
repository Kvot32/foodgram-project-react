from django.contrib import admin
from .models import  Favorite, TagsModel, RecipesModel, IngredientsModel, ShoppingCart, RecipeIngredient


admin.site.register(TagsModel)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipesModel.ingredients.through
    extra = 1


class RecipeTagAdmin(admin.TabularInline):
    model = RecipesModel.tags.through
    extra = 1

@admin.register(RecipesModel)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author','image',
                    'text', 'cooking_time',)
    list_display_links = ('name',)
    list_filter = ('name', 'author__username', 'tags')
    search_fields = ('name',)
    inlines = (RecipeIngredientAdmin,)
    readonly_fields = ('in_favorite',)

    def in_favorite(self, obj):
        return obj.in_favorite.count()


@admin.register(RecipeIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = ('amount','ingredient',)



@admin.register(IngredientsModel)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

@admin.register(ShoppingCart)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')



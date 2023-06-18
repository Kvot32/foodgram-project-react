import django_filters as filters
from recipes.models import IngredientsModel, RecipesModel


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr="iexact",
        label='Tags',
    )
    is_favorited = filters.BooleanFilter(
        method='get_favorite',
        label='Favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping',
        label='Is in shopping list',
    )

    class Meta:
        model = RecipesModel
        fields = (
            'is_favorited',
            'author',
            'tags',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, value):
        if value:
            queryset = queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def get_shopping(self, queryset, value):
        if value:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = IngredientsModel
        fields = ('name',)

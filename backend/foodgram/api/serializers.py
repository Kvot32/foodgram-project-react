from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from users.models import Follow, UserModel
from recipes.models import Recipe, Tag, Ingredient, AmountIngredient, Favorite, ShoppingList
import base64


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тего"""

    class Meta:
        model = Tag
        fields = ('name', 'color', 'id', 'slug')
        ordering = ('-id',)


class CustomUserSerializer(UserCreateSerializer):
    """Сериализатор для пользователей"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = UserModel
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'password')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        ordering = ('name',)


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор для количества ингредиентов"""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    """Добавление ингредиентов и их количество при создании рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount',)


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинки (из теории)"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = Recipe
        ordering = ('-id',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок"""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.author.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return FavoriteRecipeSerializer(queryset, many=True).data


class FavoriteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Favorite
        fields = ('user', 'id', 'image', 'cooking_time')


class RecipesGetSerializer(serializers.ModelSerializer):
    """Сериализатор для GET метода"""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientGetSerializer(many=True, source='ingredientrecipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'author',
                  'image',
                  'ingredients',
                  'text',
                  'cooking_time',
                  'tags',
                  'is_favorited',
                  'is_in_shopping_cart',
                  )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj.author
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists()


class RecipeCreatedSerializer(serializers.ModelSerializer):
    """Сериализатор для POST, PATCH"""
    ingredients = RecipeIngredientPostSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    author = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user
            , author=obj.author
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=user,
            recipe=obj.recipe
        ).exists()

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            ingredient_id = ingredient.get('ingredient').id
            amount = ingredient.get('amount')
            AmountIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_id,
                amount=amount
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipesGetSerializer(instance).data

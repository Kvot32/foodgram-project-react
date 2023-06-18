from django.contrib.auth import get_user_model
from django.db.models import Sum

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .filters import RecipeFilter
from .services import create_shopping_list
from .paginator import LimitPageNumberPagination
from .serializers import TagSerializer, IngredientSerializer, FavoriteSerializer, RecipeIngredientGetSerializer, \
    FollowSerializer, CustomUserSerializer, RecipesGetSerializer, RecipeCreatedSerializer
from rest_framework import viewsets, status
from recipes.models import Favorite, TagsModel, RecipesModel, IngredientsModel, ShoppingCart, RecipeIngredient
from users.models import Follow
from rest_framework.decorators import action
from djoser.views import UserViewSet
from .permissions import AdminUserOrReadOnly

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminUserOrReadOnly,)
    queryset = TagsModel.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = IngredientsModel.objects.all()
    serializer_class = IngredientSerializer


class AmountIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientGetSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPagination
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('username',)
    serializers_class = CustomUserSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(user)
        serializer = FollowSerializer(pages, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.filter(user=user, author=author)
            if follow.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.create(user=user, author=author)
            serializers = FollowSerializer(
                follow, context={'request': request})
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user is author:
                return Response(
                    {'errors': 'Вы не можете отписаться от самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.filter(user=user, author=author)
            if not follow.exists():
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = RecipesModel.objects.all()
    permission_classes = [AllowAny, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesGetSerializer
        return RecipeCreatedSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPageNumberPagination
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(RecipesModel, pk=pk)
        favorited = Favorite.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if favorited.exists():
                return Response(
                    {'error': 'Вы уже добавили рецепт в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializers = FavoriteSerializer(
                recipe, context={'request': request})
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not favorited.exists():
                return Response(
                    {'error': 'Этого рецепта не в вашем списке избраного.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorited.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPageNumberPagination
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(RecipesModel, pk=pk)
        in_shopping = ShoppingCart.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if in_shopping.exists():
                return Response(
                    {'error': 'Вы уже добавили рецепт в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializers = FavoriteSerializer(
                recipe, context={'request': request})
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not in_shopping.exists():
                return Response(
                    {'error': 'У вас нет этого рецепта в списоке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            in_shopping.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
        pagination_class=LimitPageNumberPagination
    )
    def get_shopping_card(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_list__user=user).values(
            'ingredients__name',
            'ingredients__measurement_unit').order_by(
            'ingredients__name').annotate(total=Sum('amount'))
        return create_shopping_list(ingredients)

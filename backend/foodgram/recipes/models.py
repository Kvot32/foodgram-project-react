from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


from users.models import UserModel

class TagsModel (models.Model):
    name = models.CharField (max_length=80, verbose_name='Название', unique=True)
    color = models.CharField (max_length=7, unique=True,
                              validators=[RegexValidator (regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                                                          message='Ваше значение не является цветом'
                                                          )]
                              )
    slug = models.SlugField (
        max_length=200,
        verbose_name="Cлаг",
        unique=True,
    )
    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
    def __str__ (self):
        return self.slug
class RecipeIngredient (models.Model):
    ingredient = models.ForeignKey ('IngredientsModel', verbose_name='Ингридиент', related_name='ingredients',
                                    on_delete=models.CASCADE
                                    )
    amount = models.IntegerField (validators=[MinValueValidator (1)], verbose_name='Количество в рецепте')
    recipe = models.ForeignKey ('RecipesModel', on_delete=models.CASCADE, related_name='ingredientrecipes',
                                verbose_name='Рецепт'
                                )
    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
    def __str__ (self):
        return f'{self.ingredient}, {self.amount}'
class IngredientsModel (models.Model):
    name = models.CharField (max_length=200, verbose_name='Название ингридиента')
    measurement_unit = models.CharField (max_length=200, verbose_name='Еденица измерения')
    class Meta:
        ordering = ("name",)
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингидиенты"
    def __str__ (self):
        return f'{self.name}, {self.measurement_unit}'
class RecipesModel (models.Model):
    name = models.CharField (max_length=200, verbose_name='Название')
    author = models.ForeignKey (
        UserModel, related_name='recipes', on_delete=models.CASCADE, verbose_name='автор'
    )
    image = models.ImageField (upload_to='image/', verbose_name='Фото рецепта')
    ingredients = models.ManyToManyField (IngredientsModel, through=RecipeIngredient,
                                         verbose_name='Количество ингридиентов', )
    text = models.TextField (verbose_name='Текст')
    cooking_time = models.PositiveSmallIntegerField (default=1, validators=[MinValueValidator (1)],
                                                     verbose_name='Время готовки'
                                                     )
    tags = models.ManyToManyField (TagsModel, verbose_name='Теги',
                                  related_name='recipes'
                                  )
    class Meta:
        ordering = ("name",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
    def __str__ (self):
        return self.name
class Favorite (models.Model):
    user = models.ForeignKey (UserModel, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey (RecipesModel, on_delete=models.CASCADE, related_name='favorites')
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint (
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]
class ShoppingCart (models.Model):
    user = models.ForeignKey (UserModel, on_delete=models.CASCADE)
    recipe = models.ForeignKey (RecipesModel, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'Шопинг лист'
        constraints = [
            models.UniqueConstraint (
                fields=['user', 'recipe'],
                name='unique_list_recipe'
            )
        ]

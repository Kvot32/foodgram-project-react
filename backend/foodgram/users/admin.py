from django.contrib import admin
from .models import UserModel, Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    model = UserModel
    list_display = ('username', 'email', 'last_name', 'password',)

"""
URL configuration for gastrognome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from gastrognome_api import views

router = DefaultRouter(trailing_slash=False)
router.register(r'recipes', views.RecipeView, 'recipe')
router.register(r'ingredients', views.IngredientView, 'ingredient')
router.register(r'genres', views.GenreView, 'genre')
router.register(r'categories', views.CategoryView, 'category')
router.register(r'category_types', views.CategoryTypeView, 'category_type')
router.register(r'users', views.UserView, 'user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', views.register_user),
    path('login', views.login_user),
    path('', include(router.urls)),
]

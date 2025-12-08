from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "hezora"

urlpatterns = [
    path("", views.index, name="index"),
    path("book/<int:pk>/", views.book_detail, name="book_detail"),
    path("book/<int:pk>/download/", views.download_book, name="download_book"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("library/", views.library_view, name="library"),
    path("favorites/", views.favorites_view, name="favorites"),
    path("favorites/add/<int:pk>/", views.add_to_favorites, name="add_to_favorites"),
    path("checkout/", views.checkout, name="checkout"),
    path("signup/", views.signup, name="signup"),
    path('login/', auth_views.LoginView.as_view(template_name='hezora/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
]

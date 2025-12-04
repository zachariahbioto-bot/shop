from django.urls import path
from . import views

app_name = "hezora"

urlpatterns = [
    path("", views.index, name="index"),
    path("book/<int:pk>/", views.book_detail, name="book_detail"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment/simulate/<int:order_id>/", views.simulate_payment, name="simulate_payment"),
]

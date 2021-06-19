from django.urls import path
from .views import ProductView, ShopView, ShopCart, CartPrice, SubscriptionPrice, SubscriptionPricing

urlpatterns = [
    path('<int:product_id>', ProductView.as_view()),
    path('search', ShopView.as_view()),
    path('products', ShopCart.as_view()),
    path('cart/price', CartPrice.as_view()),
    path('subscription/price', SubscriptionPrice.as_view()),
    path('subscription/pricing', SubscriptionPricing.as_view()),
]

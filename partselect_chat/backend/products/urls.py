from django.urls import path
from .views import ProductSearchView, CompatibilityCheckView

urlpatterns = [
    path('search/', ProductSearchView.as_view(), name='product-search'),
    path('compatibility/', CompatibilityCheckView.as_view(), name='compatibility-check'),
]
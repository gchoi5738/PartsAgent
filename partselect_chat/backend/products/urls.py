from django.urls import path
from .views import (
    ProductSearchView, CompatibilityCheckView,
    ProductDetailView, InstallationGuideView
)

app_name = 'products'

urlpatterns = [
    path('search/', ProductSearchView.as_view(), name='product-search'),
    path('compatibility/', CompatibilityCheckView.as_view(), name='compatibility-check'),
    path('<str:part_number>/', ProductDetailView.as_view(), name='product-detail'),
    path('<str:part_number>/installation-guide/', InstallationGuideView.as_view(), name='installation-guide'),
]

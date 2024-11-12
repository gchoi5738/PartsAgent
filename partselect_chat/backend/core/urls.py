from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', include('chat.urls', namespace='chat')),
    path('api/products/', include('products.urls', namespace='products')),
]

from rest_framework import serializers
from .models import Product, InstallationGuide, ModelCompatibility

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'part_number', 'name', 'description', 'appliance_type', 
                 'price', 'stock_quantity']

class InstallationGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallationGuide
        fields = ['id', 'product', 'content']

class ModelCompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCompatibility
        fields = ['id', 'product', 'model_number', 'brand', 'notes']
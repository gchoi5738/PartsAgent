from rest_framework import serializers
from .models import Product, InstallationGuide, ModelCompatibility


class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = [
        'id', 'part_number', 'name', 'description',
        'appliance_type', 'price', 'stock_quantity',
        'created_at', 'updated_at'
    ]


class InstallationGuideSerializer(serializers.ModelSerializer):
  product = ProductSerializer(read_only=True)  # Nested serializer for product

  class Meta:
    model = InstallationGuide
    fields = ['id', 'content', 'product']


class ModelCompatibilitySerializer(serializers.ModelSerializer):
  product_details = ProductSerializer(source='product', read_only=True)

  class Meta:
    model = ModelCompatibility
    fields = [
        'id', 'product', 'product_details', 'model_number',
        'brand', 'notes', 'created_at', 'updated_at'
    ]


class ProductSearchResultSerializer(serializers.Serializer):
  id = serializers.IntegerField()
  part_number = serializers.CharField()
  name = serializers.CharField()
  description = serializers.CharField()
  price = serializers.DecimalField(max_digits=10, decimal_places=2)
  similarity_score = serializers.FloatField()
  appliance_type = serializers.CharField()

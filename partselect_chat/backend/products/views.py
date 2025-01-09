from rest_framework import views, generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async, async_to_sync
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Product, InstallationGuide
from .serializers import (
    ProductSerializer, InstallationGuideSerializer,
    ProductSearchResultSerializer
)
from .services.product_service import ProductService


@method_decorator(csrf_exempt, name='dispatch')
class ProductSearchView(views.APIView):
  product_service = None

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.product_service = ProductService()

  def post(self, request, *args, **kwargs):
    query = request.data.get('query')
    limit = request.data.get('limit', 5)
    appliance_type = request.data.get('appliance_type')

    if not query:
      return Response(
          {'error': 'Query is required'},
          status=status.HTTP_400_BAD_REQUEST
      )

    try:
      # Convert async to sync
      search_products_sync = async_to_sync(self.product_service.search_products)
      products = search_products_sync(
          query,
          limit=limit,
          appliance_type=appliance_type
      )

      serializer = ProductSearchResultSerializer(products, many=True)
      return Response(serializer.data)
    except Exception as e:
      return Response(
          {'error': str(e)},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )


class ProductDetailView(generics.RetrieveAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
  lookup_field = 'part_number'


@method_decorator(csrf_exempt, name='dispatch')
class CompatibilityCheckView(views.APIView):
  product_service = None

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.product_service = ProductService()

  def post(self, request, *args, **kwargs):
    part_number = request.data.get('part_number')
    model_number = request.data.get('model_number')

    if not part_number or not model_number:
      return Response(
          {'error': 'Both part_number and model_number are required'},
          status=status.HTTP_400_BAD_REQUEST
      )

    try:
      check_compatibility_sync = async_to_sync(self.product_service.check_compatibility)
      result = check_compatibility_sync(part_number, model_number)
      return Response(result)
    except Exception as e:
      return Response(
          {'error': str(e)},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )


class InstallationGuideView(views.APIView):
  product_service = None

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.product_service = ProductService()

  def get(self, request, part_number, *args, **kwargs):
    try:
      print(f"Fetching installation guide for part number: {part_number}")
      guide_data = async_to_sync(self.product_service.get_installation_guide)(part_number)

      if not guide_data:
        return Response(
            {'error': 'No installation guide found for this part'},
            status=status.HTTP_404_NOT_FOUND
        )

      # Get the actual InstallationGuide object
      product = Product.objects.get(part_number=part_number)
      guide = InstallationGuide.objects.get(product=product)

      serializer = InstallationGuideSerializer(guide)
      return Response(serializer.data)

    except Product.DoesNotExist:
      return Response(
          {'error': 'Product not found'},
          status=status.HTTP_404_NOT_FOUND
      )
    except InstallationGuide.DoesNotExist:
      return Response(
          {'error': 'Installation guide not found'},
          status=status.HTTP_404_NOT_FOUND
      )
    except Exception as e:
      print(f"Error in InstallationGuideView: {str(e)}")
      return Response(
          {'error': str(e)},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )


class ProductListView(generics.ListAPIView):
  serializer_class = ProductSerializer

  def get_queryset(self):
    queryset = Product.objects.all()
    appliance_type = self.request.query_params.get('appliance_type', None)

    if appliance_type:
      queryset = queryset.filter(appliance_type=appliance_type)

    return queryset

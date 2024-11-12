from django.shortcuts import render

# Create your views here.
from rest_framework import views, status
from rest_framework.response import Response
from .services.product_service import ProductService
from .serializers import ProductSerializer

class ProductSearchView(views.APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_service = ProductService()

    async def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response(
                {'error': 'Query is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            products = await self.product_service.search_products(query)
            return Response(products)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompatibilityCheckView(views.APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_service = ProductService()

    async def post(self, request):
        part_number = request.data.get('part_number')
        model_number = request.data.get('model_number')
        
        if not part_number or not model_number:
            return Response(
                {'error': 'Both part_number and model_number are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = await self.product_service.check_compatibility(
                part_number, model_number
            )
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
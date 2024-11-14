from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
from django.conf import settings
from asgiref.sync import sync_to_async
from pgvector.django import L2Distance

from ..models import Product, ProductDocument, InstallationGuide, ModelCompatibility


class ProductService:
  def __init__(self):
    self.embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY
    )

  async def search_products(
      self,
      query: str,
      limit: int = 5,
      appliance_type: Optional[str] = None,
      similarity_threshold: float = 0.7
  ) -> List[Dict]:
    try:
      # Structure query to emphasize part numbers if present
      import re
      part_number_match = re.search(r'[A-Z]+\d{4,}[A-Z]*', query.upper())
      if part_number_match:
        query = f"PART_NUMBER: {part_number_match.group()}"

      query_embedding = await self.embeddings.aembed_query(query)

      queryset = Product.objects.annotate(
          distance=L2Distance('document__embedding', query_embedding)
      ).select_related('document')

      if appliance_type:
        queryset = queryset.filter(appliance_type=appliance_type)

      products = await sync_to_async(list)(
          queryset.filter(distance__lte=similarity_threshold)
          .order_by('distance')[:limit]
      )

      # Fetch installation guide content in a separate query
      product_ids = [p.id for p in products]
      installation_guides = await sync_to_async(list)(
          InstallationGuide.objects.filter(product_id__in=product_ids)
      )
      installation_guide_map = {ig.product_id: ig.content for ig in installation_guides}

      return [
          {
              'id': p.id,
              'part_number': p.part_number,
              'name': p.name,
              'description': p.description,
              'price': p.price,
              'appliance_type': p.appliance_type,
              'similarity_score': float(p.distance),
              'installation_guide': installation_guide_map.get(p.id, None),
              'stock_quantity': p.stock_quantity,
          }
          for p in products
      ]
    except Exception as e:
      print(f"Error in search_products: {str(e)}")
      raise Exception(f"Error searching products: {str(e)}")

  async def get_relevant_context(self, query: str) -> Dict:
    """Get all relevant context for a query"""
    try:
      print("\n=== Search Debug ===")
      print(f"Query: '{query}'")

      # Search for products with their guides included
      products = await self.search_products(query, limit=3)

      # Get compatibility information for each product
      for product in products:
        compatibility_info = await self.check_compatibility(product['part_number'], None)
        product['compatibility_info'] = compatibility_info['compatible_models']

      print("\nFound Products:")
      for p in products:
        print(f"- {p['part_number']}: {p['name']} (score: {p['similarity_score']:.4f})")
        print("  Compatible Models:")
        for model in p['compatibility_info']:
          print(f"  - {model['model_number']} ({model['brand']})")
        if p['installation_guide']:
          print("  Installation Guide: Available")
        else:
          print("  Installation Guide: Not Available")

      print("==================\n")

      return {
          'products': products,
          'installation_guides': [p['installation_guide'] for p in products if p['installation_guide']],
          'compatibility_info': [p['compatibility_info'] for p in products]
      }
    except Exception as e:
      print(f"Error in get_relevant_context: {str(e)}")
      raise Exception(f"Error getting relevant context: {str(e)}")

  async def check_compatibility(self, part_number: str, model_number: str) -> Dict:
    """Get compatibility information for a product"""
    try:
        # First find the product
      products = await self.search_products(f"PART_NUMBER: {part_number}", limit=1)
      if not products:
        return {
            'is_compatible': False,
            'notes': 'Part number not found',
            'product_details': None,
            'compatibility_info': None
        }

      # Get all compatibility information for this product
      product = await sync_to_async(Product.objects.get)(id=products[0]['id'])
      compatibilities = await sync_to_async(list)(
          ModelCompatibility.objects.filter(product=product)
          .values('model_number', 'brand', 'notes')
      )

      print(f"Compatible models for {part_number}:")
      for c in compatibilities:
        print(f"- {c['model_number']} ({c['brand']})")

      return {
          'product_details': {
              'part_number': product.part_number,
              'name': product.name,
              'appliance_type': product.appliance_type,
              'description': product.description
          },
          'compatible_models': compatibilities  # Let the LLM analyze this
      }
    except Exception as e:
      return {
          'is_compatible': False,
          'notes': f'Error checking compatibility: {str(e)}',
          'product_details': None,
          'compatibility_info': None
      }

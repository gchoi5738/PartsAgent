from django.core.management.base import BaseCommand
from django.db import transaction
from asgiref.sync import sync_to_async
from products.models import Product, InstallationGuide
from products.services.product_service import ProductService
import asyncio


class Command(BaseCommand):
  help = 'Create vector embeddings for products and guides'

  def handle(self, *args, **kwargs):
    service = ProductService()

    async def create_all_embeddings():
      # Get all products using sync_to_async
      products = await sync_to_async(list)(Product.objects.all())
      self.stdout.write(f'Found {len(products)} products')

      for product in products:
        try:
          await service.create_product_embedding(product)
          self.stdout.write(f'Created embedding for product {product.part_number}')
        except Exception as e:
          self.stdout.write(
              self.style.ERROR(
                  f'Error creating embedding for {product.part_number}: {str(e)}'
              )
          )

      # Get all guides using sync_to_async
      guides = await sync_to_async(list)(InstallationGuide.objects.all())
      self.stdout.write(f'Found {len(guides)} installation guides')

      for guide in guides:
        try:
          await service.create_guide_embedding(guide)
          self.stdout.write(
              f'Created embedding for guide of {guide.product.part_number}'
          )
        except Exception as e:
          self.stdout.write(
              self.style.ERROR(
                  f'Error creating embedding for guide: {str(e)}'
              )
          )

    # Run the async function
    asyncio.run(create_all_embeddings())
    self.stdout.write(self.style.SUCCESS('Successfully created all embeddings'))

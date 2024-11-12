from django.core.management.base import BaseCommand
from products.models import Product, InstallationGuide
from products.services.product_service import ProductService
import asyncio


class Command(BaseCommand):
  help = 'Update vector store with product and guide embeddings'

  def handle(self, *args, **options):
    service = ProductService()

    async def update_all():
      # Update product documents
      products = Product.objects.all()
      for product in products:
        await service.create_or_update_document(product, 'product')
        self.stdout.write(f'Updated vector store for product {product.part_number}')

      # Update guide documents
      guides = InstallationGuide.objects.all()
      for guide in guides:
        await service.create_or_update_document(guide, 'guide')
        self.stdout.write(f'Updated vector store for guide of {guide.product.part_number}')

    asyncio.run(update_all())
    self.stdout.write(self.style.SUCCESS('Successfully updated vector store'))

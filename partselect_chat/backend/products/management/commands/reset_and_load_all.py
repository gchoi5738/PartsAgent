from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, ProductDocument, InstallationGuide, ModelCompatibility
from products.services.product_service import ProductService
import random
import asyncio
from asgiref.sync import sync_to_async


class Command(BaseCommand):
  help = 'Reset and load all product data with embeddings'

  def add_arguments(self, parser):
    parser.add_argument(
        '--no-embeddings',
        action='store_true',
        help='Skip creating embeddings (useful for testing)',
    )

  def handle(self, *args, **options):
    service = ProductService()

    refrigerator_parts = [
        {
            'part_number': 'W10295370A',
            'name': 'Refrigerator Water Filter',
            'description': 'EveryDrop Filter 1 (EDR1RXD1). Reduces contaminants, including lead, mercury, pesticides, pharmaceuticals. For Whirlpool, Maytag, Amana, KitchenAid, and JennAir side-by-side and bottom-freezer refrigerators.',
            'price': 49.99
        },
        {
            'part_number': 'W10190965',
            'name': 'Refrigerator Ice Maker Assembly',
            'description': 'Original Whirlpool ice maker assembly. Includes motor, ejector blade, and electrical harness. Produces 8 ice cubes per cycle, up to 120 cubes per day.',
            'price': 169.99
        },
        {
            'part_number': 'WP2198597',
            'name': 'Thermostat Control Board',
            'description': 'Electronic control board that regulates temperature and defrost cycles. Compatible with multiple Whirlpool and Kenmore models. Includes installation hardware.',
            'price': 225.99
        },
        {
            'part_number': 'W10518394',
            'name': 'Defrost Heater Assembly',
            'description': 'Heating element for automatic defrost system. 120V, 250W. Prevents ice buildup on evaporator coils. Includes thermal fuse for safety.',
            'price': 84.99
        },
        {
            'part_number': 'W10312695',
            'name': 'Temperature Sensor',
            'description': 'Precision thermistor for accurate temperature monitoring. 10K ohm resistance at 25°C. Used in fresh food and freezer compartments.',
            'price': 35.99
        }
    ]

    dishwasher_parts = [
        {
            'part_number': 'W10350375',
            'name': 'Dishwasher Control Board',
            'description': 'Main electronic control board for dishwasher functions. Controls wash cycles, water temperature, and all electronic operations. Includes mounting hardware and wire harness.',
            'price': 189.99
        },
        {
            'part_number': 'W10300024',
            'name': 'Spray Arm Assembly',
            'description': 'Upper spray arm with multiple water jets for thorough cleaning coverage. Includes mounting hub and water flow directors. Self-cleaning nozzles prevent clogging.',
            'price': 65.99
        },
        {
            'part_number': 'W10195416',
            'name': 'Door Latch Assembly',
            'description': 'Complete door latch mechanism with safety switch. Includes strike plate and electrical contacts. Prevents operation when door is open.',
            'price': 89.99
        },
        {
            'part_number': 'W10195417',
            'name': 'Circulation Pump Motor',
            'description': 'Main circulation pump motor assembly. 120V, 60Hz motor with built-in thermal protection. Includes mounting gaskets and hardware.',
            'price': 145.99
        },
        {
            'part_number': 'W10482550',
            'name': 'Heating Element',
            'description': 'Water heating element for wash and dry cycles. 1200W heating capacity. Includes mounting brackets and high-temperature wiring.',
            'price': 79.99
        }
    ]

    # Model compatibility data
    refrigerator_models = [
        'WRF535SMHZ', 'WRX735SDHZ', 'WRF767SDHZ', 'WRF757SDHZ',
        'MFI2570FEZ', 'MSS25N4MKZ', 'MFI2269FRZ', 'MFF2558FEZ'
    ]

    dishwasher_models = [
        'WDF520PADM', 'WDT730PAHZ', 'WDT750SAHZ', 'WDT970SAHZ',
        'MDB8959SKZ', 'MDB7959SKZ', 'MDB8979SFZ', 'MDB7979SHZ'
    ]

    async def reset_and_load():
      try:
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        await sync_to_async(ModelCompatibility.objects.all().delete)()
        await sync_to_async(InstallationGuide.objects.all().delete)()
        await sync_to_async(ProductDocument.objects.all().delete)()
        await sync_to_async(Product.objects.all().delete)()

        # Create refrigerator parts
        for part_data in refrigerator_parts:
          self.stdout.write(f"Creating refrigerator part {part_data['part_number']}...")

          # Create product
          product = await sync_to_async(Product.objects.create)(
              part_number=part_data['part_number'],
              name=part_data['name'],
              description=part_data['description'],
              appliance_type='REFRIGERATOR',
              price=part_data['price'],
              stock_quantity=random.randint(10, 50)
          )

          if not options['no_embeddings']:
            # Create embedding
            text = product.get_document_text()
            embedding = await service.embeddings.aembed_query(text)
            await sync_to_async(ProductDocument.objects.create)(
                product=product,
                embedding=embedding
            )

          # Create installation guide
          guide_content = f"""Installation Guide for {product.part_number} {product.name}

Safety First:
- Unplug refrigerator before installing
- Read all instructions carefully
- Wear protective gloves if necessary

Tools Required:
- Phillips head screwdriver
- Adjustable wrench
- Work gloves

Installation Steps:
1. Preparation
   - Remove old {product.name.lower()} if replacing
   - Clean installation area
   - Gather all necessary tools

2. Installation Process
   - Carefully remove packaging
   - Follow model-specific instructions
   - Verify all connections

3. Testing
   - Restore power
   - Test operation
   - Check for proper function

For technical support: 1-800-PARTSELECT"""

          await sync_to_async(InstallationGuide.objects.create)(
              product=product,
              content=guide_content
          )

          # Create compatibility entries
          for model in random.sample(refrigerator_models, 3):
            await sync_to_async(ModelCompatibility.objects.create)(
                product=product,
                model_number=model,
                brand='Whirlpool' if model.startswith('W') else 'Maytag',
                notes=f'Compatible with {model}'
            )

        # Create dishwasher parts
        for part_data in dishwasher_parts:
          self.stdout.write(f"Creating dishwasher part {part_data['part_number']}...")

          # Create product
          product = await sync_to_async(Product.objects.create)(
              part_number=part_data['part_number'],
              name=part_data['name'],
              description=part_data['description'],
              appliance_type='DISHWASHER',
              price=part_data['price'],
              stock_quantity=random.randint(10, 50)
          )

          if not options['no_embeddings']:
            # Create embedding
            text = product.get_document_text()
            embedding = await service.embeddings.aembed_query(text)
            await sync_to_async(ProductDocument.objects.create)(
                product=product,
                embedding=embedding
            )

          # Create installation guide
          guide_content = f"""Installation Guide for {product.part_number} {product.name}

Safety First:
- Disconnect power
- Shut off water supply if applicable
- Read all instructions

Tools Required:
- Screwdriver set
- Adjustable wrench
- Work gloves

Installation Steps:
1. Preparation
   - Remove access panels
   - Document wire connections
   - Take photos for reference

2. Installation
   - Follow model-specific instructions
   - Verify connections
   - Secure all components

3. Testing
   - Restore power
   - Run test cycle
   - Check for proper operation

For installation support: 1-800-PARTSELECT"""

          await sync_to_async(InstallationGuide.objects.create)(
              product=product,
              content=guide_content
          )

          # Create compatibility entries
          for model in random.sample(dishwasher_models, 3):
            await sync_to_async(ModelCompatibility.objects.create)(
                product=product,
                model_number=model,
                brand='Whirlpool' if model.startswith('W') else 'Maytag',
                notes=f'Compatible with {model}'
            )

      except Exception as e:
        self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
        raise e

    # Run the async function
    asyncio.run(reset_and_load())

    # Print summary
    self.stdout.write(self.style.SUCCESS('\nData load completed!'))
    self.stdout.write(f'Products: {Product.objects.count()}')
    self.stdout.write(f'Embeddings: {ProductDocument.objects.count()}')
    self.stdout.write(f'Installation Guides: {InstallationGuide.objects.count()}')
    self.stdout.write(f'Compatibility Records: {ModelCompatibility.objects.count()}')

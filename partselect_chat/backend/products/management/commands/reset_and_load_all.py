from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, ProductDocument, InstallationGuide, ModelCompatibility
from products.services.product_service import ProductService
import random
import asyncio
from asgiref.sync import sync_to_async
from faker import Faker
import json


class Command(BaseCommand):
  help = 'Generate large dataset of realistic appliance parts'

  def add_arguments(self, parser):
    parser.add_argument(
        '--count',
        type=int,
        default=300,
        help='Number of products to generate'
    )
    parser.add_argument(
        '--no-embeddings',
        action='store_true',
        help='Skip creating embeddings (useful for testing)',
    )

  def handle(self, *args, **options):
    fake = Faker()
    service = ProductService()

    # Component types and their descriptions
    REFRIGERATOR_COMPONENTS = {
        'FILTER': {
            'names': ['Water Filter', 'Air Filter', 'Carbon Filter'],
            'desc_template': 'High-quality {} designed to remove contaminants and improve {} quality. {} filtration technology with {} month lifespan.',
            'price_range': (30, 80)
        },
        'MOTOR': {
            'names': ['Evaporator Fan Motor', 'Condenser Fan Motor', 'Ice Maker Motor'],
            'desc_template': 'Reliable {} rated for {} RPM. Energy-efficient design with {} bearings and {} protection.',
            'price_range': (120, 250)
        },
        'BOARD': {
            'names': ['Control Board', 'Display Board', 'Power Board'],
            'desc_template': 'Electronic {} with {} microprocessor. Controls {} functions with {} protection features.',
            'price_range': (150, 400)
        },
        'SENSOR': {
            'names': ['Temperature Sensor', 'Defrost Sensor', 'Door Sensor'],
            'desc_template': 'Precision {} with {} accuracy. Monitors {} with {} response time.',
            'price_range': (20, 100)
        }
    }

    DISHWASHER_COMPONENTS = {
        'PUMP': {
            'names': ['Drain Pump', 'Circulation Pump', 'Wash Pump'],
            'desc_template': 'Heavy-duty {} with {} GPM flow rate. {} impeller design for {} performance.',
            'price_range': (100, 300)
        },
        'SPRAY': {
            'names': ['Upper Spray Arm', 'Lower Spray Arm', 'Middle Spray Arm'],
            'desc_template': 'Advanced {} with {} spray jets. Provides {} coverage with {} cleaning action.',
            'price_range': (40, 120)
        },
        'HEATER': {
            'names': ['Heating Element', 'Water Heater', 'Drying Element'],
            'desc_template': '{} rated at {} watts. Ensures {} temperature for {} cleaning.',
            'price_range': (60, 150)
        },
        'RACK': {
            'names': ['Upper Rack', 'Lower Rack', 'Cutlery Basket'],
            'desc_template': 'Durable {} with {} coating. Features {} adjustable positions and {} capacity.',
            'price_range': (80, 200)
        }
    }

    # Brand and model information
    BRANDS = {
        'Whirlpool': {'prefix': 'W', 'models_prefix': 'WDT'},
        'Maytag': {'prefix': 'M', 'models_prefix': 'MDB'},
        'KitchenAid': {'prefix': 'K', 'models_prefix': 'KDT'},
        'Amana': {'prefix': 'A', 'models_prefix': 'ADB'}
    }

    def generate_part_number(brand_prefix, component_type):
      return f"{brand_prefix}P{random.randint(10000, 99999)}{component_type[:2].upper()}"

    def generate_model_number(brand_prefix):
      return f"{brand_prefix}{random.randint(100, 999)}SAHZ"

    def generate_installation_guide(product, component_type):
      tools = ['Phillips screwdriver', 'Flathead screwdriver', 'Adjustable wrench',
               'Pliers', 'Socket set', 'Multimeter', 'Wire strippers']
      safety_steps = ['Disconnect power', 'Wear safety glasses', 'Use insulated tools',
                      'Remove jewelry', 'Wear work gloves', 'Ensure proper ventilation']

      return f"""Installation Guide for {product.part_number} {product.name}

Safety Instructions:
{chr(10).join(f'- {step}' for step in random.sample(safety_steps, 3))}

Tools Required:
{chr(10).join(f'- {tool}' for tool in random.sample(tools, 3))}

Installation Steps:

1. Preparation:
   - Document current installation
   - Gather required tools
   - Clear work area
   - Verify replacement part

2. Removal:
   - Follow safety procedures
   - Remove access panels
   - Disconnect electrical connections
   - Remove old component

3. Installation:
   - Verify compatibility
   - Position new {product.name}
   - Secure mounting points
   - Reconnect electrical connections

4. Testing:
   - Restore power
   - Verify operation
   - Check for proper function
   - Test all modes

Troubleshooting Tips:
- Verify all connections are secure
- Check for proper alignment
- Ensure no wires are pinched
- Confirm proper voltage

For technical support: 1-800-PARTSELECT"""

    async def generate_products(count):
      try:
        # Generate products
        for i in range(count):
          # Alternate between refrigerator and dishwasher
          is_refrigerator = i % 2 == 0

          # Select component type and details
          component_dict = REFRIGERATOR_COMPONENTS if is_refrigerator else DISHWASHER_COMPONENTS
          component_type = random.choice(list(component_dict.keys()))
          component_details = component_dict[component_type]

          # Select brand and generate numbers
          brand_name = random.choice(list(BRANDS.keys()))
          brand_info = BRANDS[brand_name]

          # Generate basic product info
          part_number = generate_part_number(brand_info['prefix'], component_type)
          name = random.choice(component_details['names'])

          # Generate description with random but relevant terms
          desc_terms = [
              random.choice(['premium', 'high-efficiency', 'advanced', 'professional-grade']),
              random.choice(['3000', '5000', '7500', '10000']),
              random.choice(['sealed', 'precision', 'balanced', 'optimized']),
              random.choice(['thermal', 'overload', 'surge', 'mechanical'])
          ]
          description = component_details['desc_template'].format(*desc_terms)

          # Create product
          price = round(random.uniform(*component_details['price_range']), 2)
          product = await sync_to_async(Product.objects.create)(
              part_number=part_number,
              name=f"{brand_name} {name}",
              description=description,
              appliance_type='REFRIGERATOR' if is_refrigerator else 'DISHWASHER',
              price=price,
              stock_quantity=random.randint(5, 100)
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
          guide_content = generate_installation_guide(product, component_type)
          await sync_to_async(InstallationGuide.objects.create)(
              product=product,
              content=guide_content
          )

          # Create compatibility entries (3-5 compatible models)
          for _ in range(random.randint(3, 5)):
            model_number = generate_model_number(brand_info['models_prefix'])
            await sync_to_async(ModelCompatibility.objects.create)(
                product=product,
                model_number=model_number,
                brand=brand_name,
                notes=f'Compatible with {model_number} series'
            )

          self.stdout.write(f'Created product {i + 1}/{count}: {part_number}')

      except Exception as e:
        self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
        raise e

    # Run the async function
    asyncio.run(generate_products(options['count']))

    # Print summary
    self.stdout.write(self.style.SUCCESS('\nData generation completed!'))
    self.stdout.write(f'Products: {Product.objects.count()}')
    self.stdout.write(f'Embeddings: {ProductDocument.objects.count()}')
    self.stdout.write(f'Installation Guides: {InstallationGuide.objects.count()}')
    self.stdout.write(f'Compatibility Records: {ModelCompatibility.objects.count()}')

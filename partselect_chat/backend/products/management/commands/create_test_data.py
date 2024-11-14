from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, InstallationGuide, ModelCompatibility
import random


class Command(BaseCommand):
  help = 'Populate database with test data'

  def handle(self, *args, **kwargs):
    self.stdout.write('Creating test data...')

    # Sample data
    refrigerator_parts = [
        {
            'name': 'Water Filter',
            'description': 'Replacement water filter that removes contaminants and improves taste. Compatible with most Whirlpool side-by-side refrigerators.',
            'price': 49.99
        },
        {
            'name': 'Ice Maker Assembly',
            'description': 'Complete ice maker assembly kit. Includes motor, blade, and electrical harness.',
            'price': 129.99
        },
        {
            'name': 'Door Shelf Bin',
            'description': 'Replacement door bin for storing gallons and larger containers. Durable clear plastic construction.',
            'price': 35.99
        },
        {
            'name': 'Temperature Control Board',
            'description': 'Electronic control board that regulates temperature. Compatible with various Whirlpool models.',
            'price': 189.99
        }
    ]

    dishwasher_parts = [
        {
            'name': 'Spray Arm',
            'description': 'Upper spray arm assembly. Ensures thorough cleaning coverage for top rack.',
            'price': 45.99
        },
        {
            'name': 'Door Latch Assembly',
            'description': 'Complete door latch mechanism with safety switch.',
            'price': 79.99
        },
        {
            'name': 'Drain Pump',
            'description': 'Replacement drain pump motor assembly. Includes mounting hardware.',
            'price': 89.99
        }
    ]

    whirlpool_models = ['WRF535SMHZ', 'WDF520PADM', 'WRX735SDHZ', 'WDT730PAHZ']
    maytag_models = ['MFI2570FEZ', 'MDB8959SKZ', 'MSS25N4MKZ', 'MDB7959SKZ']

    try:
      with transaction.atomic():
        # Create refrigerator parts
        for i, part_data in enumerate(refrigerator_parts, 1):
          part = Product.objects.create(
              part_number=f'RF{str(i).zfill(4)}',
              name=part_data['name'],
              description=part_data['description'],
              appliance_type='REFRIGERATOR',
              price=part_data['price'],
              stock_quantity=random.randint(5, 50)
          )

          # Create installation guide
          InstallationGuide.objects.create(
              product=part,
              content=f"Installation Guide for {part.name}:\n\n"
              f"1. Safety First: Unplug the refrigerator\n"
              f"2. Locate the old {part.name.lower()}\n"
              f"3. Remove the old part carefully\n"
              f"4. Install the new {part.name.lower()}\n"
              f"5. Test the installation\n\n"
              f"For more detailed instructions, consult your appliance manual."
          )

          # Create compatibility entries
          for model in whirlpool_models[:2]:
            ModelCompatibility.objects.create(
                product=part,
                model_number=model,
                brand='Whirlpool',
                notes=f'Confirmed compatible with {model}'
            )

        # Create dishwasher parts
        for i, part_data in enumerate(dishwasher_parts, 1):
          part = Product.objects.create(
              part_number=f'DW{str(i).zfill(4)}',
              name=part_data['name'],
              description=part_data['description'],
              appliance_type='DISHWASHER',
              price=part_data['price'],
              stock_quantity=random.randint(5, 50)
          )

          # Create installation guide
          InstallationGuide.objects.create(
              product=part,
              content=f"Installation Guide for {part.name}:\n\n"
              f"1. Safety Warning: Disconnect power\n"
              f"2. Access the {part.name.lower()} compartment\n"
              f"3. Remove existing part\n"
              f"4. Install new {part.name.lower()}\n"
              f"5. Verify proper operation\n\n"
              f"Warning: Professional installation recommended."
          )

          # Create compatibility entries
          for model in maytag_models[:2]:
            ModelCompatibility.objects.create(
                product=part,
                model_number=model,
                brand='Maytag',
                notes=f'Verified compatible with {model}'
            )

      self.stdout.write(self.style.SUCCESS('Successfully created test data'))

    except Exception as e:
      self.stdout.write(self.style.ERROR(f'Error creating test data: {str(e)}'))

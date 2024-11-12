from django.db import models
from pgvector.django import VectorField


class Product(models.Model):
  APPLIANCE_TYPES = [
      ('REFRIGERATOR', 'Refrigerator'),
      ('DISHWASHER', 'Dishwasher'),
  ]

  part_number = models.CharField(max_length=50, unique=True)
  name = models.CharField(max_length=200)
  description = models.TextField()
  appliance_type = models.CharField(max_length=20, choices=APPLIANCE_TYPES)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  stock_quantity = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"{self.part_number} - {self.name}"

  def get_document_text(self):
    """Get text representation for embedding"""
    return f"Product Name: {self.name}\nDescription: {self.description}\nPart Number: {self.part_number}\nType: {self.appliance_type}"


class ProductDocument(models.Model):
  """Store document embeddings for vector search"""
  product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='document')
  embedding = VectorField(dimensions=1536)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


class InstallationGuide(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='installation_guides')
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Installation Guide for {self.product.part_number}"

  def get_document_text(self):
    """Get text representation for embedding"""
    return f"Installation Guide for {self.product.part_number}\n{self.content}"


class GuideDocument(models.Model):
  """Store document embeddings for vector search"""
  guide = models.OneToOneField(InstallationGuide, on_delete=models.CASCADE, related_name='document')
  embedding = VectorField(dimensions=1536)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


class ModelCompatibility(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compatible_models')
  model_number = models.CharField(max_length=100)
  brand = models.CharField(max_length=100)
  notes = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name_plural = "Model compatibilities"
    unique_together = ['product', 'model_number']

  def __str__(self):
    return f"{self.product.part_number} - {self.model_number}"

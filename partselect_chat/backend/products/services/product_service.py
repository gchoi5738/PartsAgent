from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from django.conf import settings
from django.db import connection

from products.models import (
    Product, ProductDocument, InstallationGuide,
    GuideDocument, ModelCompatibility
)


class ProductService:
  def __init__(self):
    # Initialize LangChain components
    self.embeddings = OpenAIEmbeddings()
    self.CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver=settings.DATABASES['default']['ENGINE'].split('.')[-1],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT'],
        database=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD']
    )

    # Text splitter for long documents
    self.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

  async def create_or_update_document(self, obj, doc_type: str):
    """Create or update document embeddings"""
    # Get text representation
    text = obj.get_document_text()

    # Create document
    doc = Document(
        page_content=text,
        metadata={
            "type": doc_type,
            "id": obj.id,
            "part_number": obj.part_number if hasattr(obj, 'part_number') else obj.product.part_number
        }
    )

    # Get embedding
    embedding = await self.embeddings.aembed_query(text)

    # Store in appropriate model
    if doc_type == 'product':
      ProductDocument.objects.update_or_create(
          product=obj,
          defaults={'embedding': embedding}
      )
    else:
      GuideDocument.objects.update_or_create(
          guide=obj,
          defaults={'embedding': embedding}
      )

  async def search_products(
      self,
      query: str,
      limit: int = 5,
      appliance_type: Optional[str] = None
  ) -> List[Dict]:
    """Search products using vector similarity"""
    try:
      # Create vector store
      vector_store = PGVector(
          connection_string=self.CONNECTION_STRING,
          embedding_function=self.embeddings,
          collection_name="product_search",
          relevance_score_fn=lambda score: 1 - score  # Convert distance to similarity score
      )

      # Search
      docs = await vector_store.asimilarity_search_with_score(
          query,
          k=limit * 2  # Get extra results for filtering
      )

      # Get product details
      results = []
      for doc, score in docs:
        if doc.metadata['type'] != 'product':
          continue

        product = Product.objects.get(id=doc.metadata['id'])

        # Apply appliance type filter
        if appliance_type and product.appliance_type != appliance_type:
          continue

        results.append({
            'id': product.id,
            'part_number': product.part_number,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'appliance_type': product.appliance_type,
            'similarity_score': score
        })

        if len(results) >= limit:
          break

      return results

    except Exception as e:
      raise Exception(f"Error searching products: {str(e)}")

  async def find_relevant_guides(self, query: str, limit: int = 3) -> List[Dict]:
    """Find relevant installation guides using vector similarity"""
    try:
      vector_store = PGVector(
          connection_string=self.CONNECTION_STRING,
          embedding_function=self.embeddings,
          collection_name="guide_search"
      )

      docs = await vector_store.asimilarity_search_with_score(
          query,
          k=limit
      )

      return [
          {
              'product_part_number': guide.product.part_number,
              'content': guide.content,
              'similarity_score': score
          }
          for doc, score in docs
          if doc.metadata['type'] == 'guide'
          for guide in [InstallationGuide.objects.get(id=doc.metadata['id'])]
      ]

    except Exception as e:
      raise Exception(f"Error finding guides: {str(e)}")

  async def get_relevant_context(self, query: str) -> Dict:
    """Get all relevant context for a query"""
    products = await self.search_products(query, limit=3)
    guides = await self.find_relevant_guides(query, limit=2)

    return {
        'products': products,
        'installation_guides': guides
    }

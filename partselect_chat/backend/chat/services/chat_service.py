from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from django.conf import settings
from products.services.product_service import ProductService
import uuid
from asgiref.sync import async_to_sync
from urllib.parse import urlparse


class ChatService:
  def __init__(self):
    self.chat_model = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=settings.OPENAI_API_KEY
    )
    self.product_service = ProductService()

  def _parse_current_page(self, url: str) -> Dict:
    """Parse the current page URL to understand context"""
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')

    page_context = {
        'type': None,
        'identifier': None,
        'section': None
    }

    if 'parts' in path_parts:
      page_context['type'] = 'product'
      # Extract part number from URL
      idx = path_parts.index('parts')
      if len(path_parts) > idx + 1:
        page_context['identifier'] = path_parts[idx + 1]
    elif 'installation-guides' in path_parts:
      page_context['type'] = 'guide'
      idx = path_parts.index('installation-guides')
      if len(path_parts) > idx + 1:
        page_context['identifier'] = path_parts[idx + 1]

    return page_context

  async def get_chat_response(self, message: str, current_url: Optional[str] = None) -> Dict:
    try:
      # Get page context if URL is provided
      page_context = self._parse_current_page(current_url) if current_url else None

      # Get product context
      context = await self.product_service.get_relevant_context(message)

      # Build system message with enhanced context
      messages = [
          SystemMessage(content="""You are a helpful customer service agent for PartSelect, 
                specializing in refrigerator and dishwasher parts. You can help with:
                1. Finding the right parts
                2. Installation procedures
                3. Compatibility checks
                4. Troubleshooting guidance
                5. Navigation through product pages and guides
                        
                When asked about policies or general questions, direct users to our FAQ page at 
                http://localhost:5173/faq for detailed information.
                
                When referring to products or guides, always use http://localhost:5173 as the base URL.
                Format links as: 
                [Product Name](http://localhost:5173/products/PART_NUMBER) or 
                [Installation Guide](http://localhost:5173/products/PART_NUMBER/installation-guide)
                
                """)
      ]

      # Add page-specific context
      if page_context and page_context['type'] == 'product':
        product_info = await self.product_service.search_products(
            f"PART_NUMBER: {page_context['identifier']}",
            limit=1
        )
        if product_info:
          messages.append(SystemMessage(
              content=f"User is currently viewing product page for: {product_info[0]['name']} "
              f"(Part #{product_info[0]['part_number']})"
          ))

      # Add product context
      if context['products']:
        context_msg = "Based on the query, I found these relevant products:\n"
        for product in context['products']:
          context_msg += f"\nProduct Information:\n"
          context_msg += f"- [{product['name']}](/parts/{product['part_number']})\n"
          context_msg += f"  Price: ${product['price']}\n"
          context_msg += f"  Stock: {product['stock_quantity']} units\n"
          if product['installation_guide']:
            context_msg += f"  [View Installation Guide](/installation-guides/{product['part_number']})\n"
          context_msg += f"\n  Compatible Models:\n"
          for model in product['compatibility_info']:
            context_msg += f"    - {model['model_number']} ({model['brand']})\n"

        messages.append(SystemMessage(content=context_msg))

      # Add user message
      messages.append(HumanMessage(content=message))

      # Get response
      response = await self.chat_model.ainvoke(messages)

      return {
          'response': response.content,
          'context': context,
          'current_page': page_context
      }

    except Exception as e:
      print(f"Error in get_chat_response: {str(e)}")
      raise Exception(f"Error getting chat response: {str(e)}")

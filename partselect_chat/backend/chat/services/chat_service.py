from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from django.conf import settings
from products.services.product_service import ProductService
import uuid
from asgiref.sync import async_to_sync


class ChatService:
  def __init__(self):
    self.chat_model = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=settings.OPENAI_API_KEY
    )
    self.product_service = ProductService()

  async def get_chat_response(self, message: str) -> Dict:
    try:
      context = await self.product_service.get_relevant_context(message)

      import re
      part_numbers = re.findall(r'[A-Z]+\d{4,}[A-Z]*', message.upper())

      compatibility_info = None
      if len(part_numbers) >= 1:
        compatibility_info = await self.product_service.check_compatibility(
            part_numbers[0],
            part_numbers[1] if len(part_numbers) > 1 else None
        )

      # Build system message
      messages = [
          SystemMessage(content="""You are a helpful customer service agent for PartSelect, 
                specializing in refrigerator and dishwasher parts. Your role is to:
                1. Help customers find the right parts
                2. Explain installation procedures
                3. Check compatibility
                4. Provide troubleshooting guidance""")
      ]

      # Add context
      if context['products']:
        context_msg = "Based on the query, I found the following products:\n"
        for product in context['products']:
          context_msg += f"\nProduct Information:\n"
          context_msg += f"- {product['name']} (Part #{product['part_number']})\n"
          context_msg += f"  Price: ${product['price']}\n"
          context_msg += f"  Description: {product['description']}\n"
          context_msg += f"  Compatible Models:\n"
          for model in product['compatibility_info']:
            context_msg += f"    - {model['model_number']} ({model['brand']})\n"
          if product['installation_guide']:
            context_msg += f"\n  Installation Guide:\n{product['installation_guide']}\n"
        messages.append(SystemMessage(content=context_msg))

      # Add user message
      messages.append(HumanMessage(content=message))

      # Print the full query before sending it to the chatbot
      print("Full query being sent to the chatbot:")
      for msg in messages:
        print(f" {msg.content}")

      # Get response
      response = await self.chat_model.ainvoke(messages)

      return {
          'response': response.content,
          'context': context
      }

    except Exception as e:
      print(f"Error in get_chat_response: {str(e)}")
      raise Exception(f"Error getting chat response: {str(e)}")

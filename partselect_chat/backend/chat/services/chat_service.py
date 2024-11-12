from typing import List, Dict, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from products.services.product_service import ProductService
from chat.models import ChatSession, ChatMessage
import uuid


class ChatService:
  def __init__(self):
    self.chat_model = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.7)
    self.product_service = ProductService()

  async def get_chat_response(
      self,
      message: str,
      session_id: Optional[str] = None
  ) -> Dict:
    """Get response from the chat model with context"""
    try:
      # Get or create session
      if session_id:
        session = await ChatSession.objects.aget(session_id=session_id)
      else:
        session = await ChatSession.objects.acreate(
            session_id=str(uuid.uuid4())
        )

      # Get relevant product context
      context = await self.product_service.get_relevant_context(message)

      # Build messages list
      messages = [
          SystemMessage(content="""You are a helpful customer service agent for PartSelect, 
                specializing in refrigerator and dishwasher parts. Focus on helping customers find 
                parts, check compatibility, and provide installation guidance.""")
      ]

      # Add context if available
      if context['products'] or context['installation_guides']:
        context_msg = "Based on your question, here's what I found:\n"
        if context['products']:
          context_msg += "\nRelevant products:\n"
          for product in context['products']:
            context_msg += f"- {product['name']} (Part #{product['part_number']})\n"

        if context['installation_guides']:
          context_msg += "\nInstallation information:\n"
          for guide in context['installation_guides']:
            context_msg += f"- {guide['content']}\n"

        messages.append(SystemMessage(content=context_msg))

      # Add conversation history
      async for chat_msg in session.messages.all():
        if chat_msg.role == 'user':
          messages.append(HumanMessage(content=chat_msg.content))
        elif chat_msg.role == 'assistant':
          messages.append(AIMessage(content=chat_msg.content))

      # Add current message
      messages.append(HumanMessage(content=message))

      # Get response from LangChain
      response = await self.chat_model.agenerate([messages])
      response_text = response.generations[0][0].text

      # Save messages
      referenced_products = [p['part_number'] for p in context['products']]
      await ChatMessage.objects.abulk_create([
          ChatMessage(
              session=session,
              role='user',
              content=message,
              referenced_products=referenced_products
          ),
          ChatMessage(
              session=session,
              role='assistant',
              content=response_text,
              referenced_products=referenced_products
          )
      ])

      return {
          'session_id': session.session_id,
          'response': response_text,
          'context': context
      }

    except Exception as e:
      raise Exception(f"Error getting chat response: {str(e)}")

  async def get_chat_history(self, session_id: str) -> List[Dict]:
    """Get chat history for a session"""
    try:
      session = await ChatSession.objects.aget(session_id=session_id)
      messages = []
      async for msg in session.messages.all():
        messages.append({
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at,
            'referenced_products': msg.referenced_products
        })
      return messages
    except ChatSession.DoesNotExist:
      raise Exception("Chat session not found")

from rest_framework import views, status
from rest_framework.response import Response
from .services.chat_service import ChatService
from .serializers import ChatMessageSerializer, ChatHistorySerializer


class ChatView(views.APIView):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.chat_service = ChatService()

  async def post(self, request):
    """Handle chat messages"""
    message = request.data.get('message')
    session_id = request.data.get('session_id')

    if not message:
      return Response(
          {'error': 'Message is required'},
          status=status.HTTP_400_BAD_REQUEST
      )

    try:
      response = await self.chat_service.get_chat_response(
          message=message,
          session_id=session_id
      )
      return Response(response)
    except Exception as e:
      return Response(
          {'error': str(e)},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )


class ChatHistoryView(views.APIView):
  async def get(self, request, session_id):
    """Get chat history for a session"""
    try:
      history = await self.chat_service.get_chat_history(session_id)
      serializer = ChatHistorySerializer(history, many=True)
      return Response(serializer.data)
    except Exception as e:
      return Response(
          {'error': str(e)},
          status=status.HTTP_404_NOT_FOUND
      )

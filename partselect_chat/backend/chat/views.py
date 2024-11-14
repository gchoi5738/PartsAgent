from rest_framework import views, status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
from .services.chat_service import ChatService


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(views.APIView):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.chat_service = ChatService()

  def post(self, request):  # Changed from async def to def
    message = request.data.get('message')
    if not message:
      return Response(
          {'error': 'Message is required'},
          status=status.HTTP_400_BAD_REQUEST
      )

    try:
      # Convert async to sync
      get_response = async_to_sync(self.chat_service.get_chat_response)
      response = get_response(message)
      return Response(response)
    except Exception as e:
      return Response(
          {'error': str(e)},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

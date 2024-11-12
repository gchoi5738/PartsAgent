from django.urls import path
from .views import ChatView, ChatHistoryView

app_name = 'chat'

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
    path('history/<str:session_id>/', ChatHistoryView.as_view(), name='chat-history'),
]

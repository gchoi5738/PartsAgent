from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
  class Meta:
    model = ChatMessage
    fields = ['role', 'content', 'created_at', 'referenced_products']


class ChatHistorySerializer(serializers.ModelSerializer):
  messages = ChatMessageSerializer(many=True, read_only=True)

  class Meta:
    model = ChatSession
    fields = ['session_id', 'created_at', 'messages']

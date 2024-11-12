from django.db import models
from django.contrib.postgres.fields import ArrayField


class ChatSession(models.Model):
  session_id = models.CharField(max_length=100, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Chat Session {self.session_id}"


class ChatMessage(models.Model):
  ROLE_CHOICES = [
      ('user', 'User'),
      ('assistant', 'Assistant'),
      ('system', 'System'),
  ]

  session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
  role = models.CharField(max_length=10, choices=ROLE_CHOICES)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  # Store referenced products/guides for context
  referenced_products = ArrayField(
      models.CharField(max_length=50),
      blank=True,
      null=True
  )

  class Meta:
    ordering = ['created_at']

  def __str__(self):
    return f"{self.role} message in {self.session}"

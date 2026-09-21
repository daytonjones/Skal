from django.db import models
from django.conf import settings


class AIUsage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_usages',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.CharField(max_length=20)
    model = models.CharField(max_length=60)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    @property
    def total_tokens(self):
        return self.input_tokens + self.output_tokens


class ChatMessage(models.Model):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_CHOICES = [(ROLE_USER, "User"), (ROLE_ASSISTANT, "Assistant")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    pending_recipe = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"

from rest_framework import serializers

from apps.ai.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "pending_recipe", "created_at"]
        read_only_fields = fields


class ChatMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField()

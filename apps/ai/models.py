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

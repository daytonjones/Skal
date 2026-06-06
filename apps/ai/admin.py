from django.contrib import admin
from .models import AIUsage


@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'provider', 'model', 'input_tokens', 'output_tokens')
    list_filter = ('provider', 'user')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'created_at', 'provider', 'model', 'input_tokens', 'output_tokens')

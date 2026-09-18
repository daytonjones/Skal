from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class VersionView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"version": settings.APP_VERSION})

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import IsApproved
from apps.yeast.views import YEASTS


class YeastListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsApproved]

    def get(self, request):
        return Response(YEASTS)

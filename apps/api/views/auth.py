from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.api.permissions import IsApproved
from apps.api.serializers.auth import (
    ApprovedTokenObtainPairSerializer,
    MeSerializer,
    RegisterSerializer,
)


class ApprovedTokenObtainPairView(TokenObtainPairView):
    serializer_class = ApprovedTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved]

    def get_object(self):
        return self.request.user

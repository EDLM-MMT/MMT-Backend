from knox.auth import TokenAuthentication
from knox.views import LoginView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from users.serializers import MMTUserSerializer


class GenerateAPIKeyFromOtherAuthMethod(LoginView):
    """
    This API is for generating API Keys using Django-Rest-Knox without
    allowing an API Key to be used to generate a new API Key
    """

    def get_authenticators(self):
        """Overrides method to remove Token Authentication from available
        authentication methods"""
        return [auth for auth in super().get_authenticators() if not
                isinstance(auth, TokenAuthentication)]


class ValidateSession(generics.RetrieveAPIView):
    """
    View to get User Info and validate connection
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MMTUserSerializer

    def get_object(self):
        return self.request.user

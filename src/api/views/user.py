from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from api.serializers import LoginSerializer
from django.contrib.auth import login


class Auth(APIView):
    """
    Login an existing user
    """
    permission_classes = () # open to everyone

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            # Persist in session
            login(request, serializer.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


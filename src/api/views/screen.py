from rest_framework.generics import RetrieveAPIView
from api.serializers import ScreenSerializer
from screen.models import Screen
from django.http import Http404


class ScreenDetails(RetrieveAPIView):
    """
    Retrieve details for a screen + widgets
    """
    serializer_class = ScreenSerializer

    def get_object(self):
        try:
            return self.request.user.screens.get(slug=self.kwargs['slug'])
        except Screen.DoesNotExist:
            raise Http404

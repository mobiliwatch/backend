from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView
from api.serializers import ScreenLightSerializer, ScreenSerializer, get_widget_serializer
from screen.models import Screen
from django.http import Http404

class ScreenMixin(object):
    """
    Load screen from slug in url
    """
    def get_screen(self):
        try:
            return self.request.user.screens.get(slug=self.kwargs['slug'])
        except Screen.DoesNotExist:
            raise Http404

class ScreenList(ScreenMixin, ListAPIView):
    """
    List simplified screens
    """
    serializer_class = ScreenLightSerializer

    def get_queryset(self):
        return self.request.user.screens.all()

class ScreenDetails(ScreenMixin,RetrieveAPIView):
    """
    Retrieve details for a screen + widgets
    """
    serializer_class = ScreenSerializer

    def get_object(self):
        return self.get_screen()

class ScreenShared(RetrieveAPIView):
    """
    Retrieve details for a screen + widgets
    as an anonymous user, with a token
    """
    serializer_class = ScreenSerializer
    permission_classes = () # open !

    def get_object(self):
        # Load screen with slug + token
        try:
            return Screen.objects.get(slug=self.kwargs['slug'], token=self.kwargs['token'])
        except Screen.DoesNotExist:
            raise Http404

class WidgetUpdate(ScreenMixin, UpdateAPIView):

    def get_serializer_class(self):
        return get_widget_serializer(self.get_object())

    def get_object(self):
        """
        Load widget from screen
        """
        screen = self.get_screen()
        widgets = dict([(str(w.id), w) for w in screen.all_widgets])
        widget_id = self.kwargs['widget']
        if widget_id not in widgets:
            raise Http404
        return widgets[widget_id]

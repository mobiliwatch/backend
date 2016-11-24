from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from api.serializers import ScreenSerializer, get_widget_serializer
from screen.models import Screen, Widget
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

class ScreenDetails(ScreenMixin,RetrieveAPIView):
    """
    Retrieve details for a screen + widgets
    """
    serializer_class = ScreenSerializer

    def get_object(self):
        return self.get_screen()

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

from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.exceptions import APIException
from api.serializers import ScreenLightSerializer, ScreenSerializer, get_widget_serializer, GroupSerializer, WidgetCreationSerializer
from screen.models import Screen, Group, LocationWidget, WeatherWidget, NoteWidget, ClockWidget
from django.http import Http404
from rest_framework.response import Response

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

class WidgetManage(ScreenMixin, UpdateAPIView, DestroyAPIView):
    """
    Manage existing widget
    * update settings
    * delete it
    """

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

class WidgetCreate(ScreenMixin, CreateAPIView):
    """
    Create a new widget in a screen's group
    """
    serializer_class = WidgetCreationSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check group is in screen
        screen = self.get_screen()
        group = serializer.validated_data['group']
        if group.screen != screen:
            raise APIException('Invalid group')

        # Build widget
        # TODO: move in central controller
        widget_type = serializer.validated_data['widget_type']
        last_location = self.request.user.locations.last()
        if widget_type == 'note':
            w = NoteWidget()
        elif widget_type == 'weather':
            if not last_location:
                raise APIException('Missing location')
            w = WeatherWidget(city=last_location.city)
        elif widget_type == 'clock':
            w = ClockWidget()
        elif widget_type == 'location':
            if not last_location:
                raise APIException('Missing location')
            w = LocationWidget(location=last_location)
        else:
            raise APIException('Invalid widget type')

        w.group = group
        w.save()

        # Output widget
        serializer = get_widget_serializer(w)(instance=w)
        return Response(serializer.data, status=201)


class GroupManage(ScreenMixin, CreateAPIView, DestroyAPIView, UpdateAPIView):
    """
    Manage a group in a screen
    * Add sub group
    * Destroy group + widgets
    """
    serializer_class = GroupSerializer

    def get_queryset(self):
        screen = self.get_screen()
        return screen.groups.all()

    def create(self, *args, **kwargs):
        """
        Create sub group
        """
        group = self.get_object()
        new_group = Group.objects.create(screen=group.screen, parent=group, position=group.groups.count())

        return Response(self.get_serializer(instance=new_group).data)


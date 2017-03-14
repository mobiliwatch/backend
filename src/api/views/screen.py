from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.exceptions import APIException
from api.serializers import ScreenLightSerializer, ScreenSerializer, get_widget_serializer, GroupSerializer, WidgetCreationSerializer, ScreenCreationSerializer
from screen.models import Screen, Group, LocationWidget, WeatherWidget, NoteWidget, ClockWidget, DisruptionWidget, TwitterWidget
from django.http import Http404
from django.db.models import Max
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

class TemplateManage(ListAPIView, CreateAPIView):
    """
    Manage screen templates:
     * List simplified templates
     * Create new screen from a template
    """
    serializer_class = ScreenLightSerializer

    def get_queryset(self):
        return Screen.objects.filter(is_template=True)

    def create(self, request, *args, **kwargs):
        # Check input
        serializer = ScreenCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        template = data['template']
        assert template.is_template
        location = data['location']
        if location.user != self.request.user:
            raise APIException('Invalid location')

        # Create new screen
        screen = Screen(name=data['name'])
        screen.user = self.request.user
        screen.slugify()
        screen.save()
        screen.clone_widgets(template, location)

        # Output serialized new screen
        serializer = ScreenLightSerializer(instance=screen, context={'request': request})
        return Response(serializer.data, status=201)


class ScreenManage(ScreenMixin, RetrieveAPIView, UpdateAPIView):
    """
    Manage a screen + widgets:
     * Retrieve details
     * Update screen
    """
    serializer_class = ScreenSerializer

    def get_object(self):
        return self.get_screen()

    def perform_update(self, *args, **kwargs):
        # Standard update
        super(ScreenManage, self).perform_update(*args, **kwargs)

        # Send WS update too
        self.get_object().send_ws_update()


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

    def perform_update(self, *args, **kwargs):
        # Standard update
        super(WidgetManage, self).perform_update(*args, **kwargs)

        # Update screen
        self.get_screen().send_ws_update()

    def perform_destroy(self, *args, **kwargs):
        # Standard update
        super(WidgetManage, self).perform_destroy(*args, **kwargs)

        # Update screen
        self.get_screen().send_ws_update()

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
        widget_type = widget_type.lower().replace('widget', '')
        last_location = self.request.user.locations.last()
        if widget_type == 'note':
            w = NoteWidget()
        elif widget_type == 'twitter':
            # Check current user has twitter auth
            if not self.request.user.has_twitter_auth():
                raise APIException(_('No twitter credentials: you need to connect your Twitter account.'))
            w = TwitterWidget()

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
        elif widget_type == 'disruption':
            if not last_location:
                raise APIException('Missing location')
            w = DisruptionWidget(location=last_location)
        else:
            raise APIException('Invalid widget type')

        w.position = serializer.validated_data.get('position', len(group.list_widgets()))
        w.group = group
        w.save()

        # Send initial data to screens
        serializer = get_widget_serializer(w)(instance=w)
        w.send_ws_update(serializer.data)

        # Send structure update
        w.group.screen.send_ws_update()

        # Output widget
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
        # Find max position
        group = self.get_object()
        max_pos = group.groups.all().aggregate(Max('position'))
        position = (max_pos['position__max'] or 0) + 1

        # Create group
        new_group = Group.objects.create(screen=group.screen, parent=group, position=position)

        # Update screen
        group.screen.send_ws_update()

        return Response(self.get_serializer(instance=new_group).data)

    def perform_update(self, *args, **kwargs):
        # Standard update
        super(GroupManage, self).perform_update(*args, **kwargs)

        # Update screen
        self.get_screen().send_ws_update()

    def perform_destroy(self, *args, **kwargs):
        # Standard update
        super(GroupManage, self).perform_destroy(*args, **kwargs)

        # Update screen
        self.get_screen().send_ws_update()

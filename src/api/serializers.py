from transport.models import Stop, LineStop, Line, Direction
from users.models import Location
from screen.models import Screen, ClockWidget, WeatherWidget, LocationWidget, NoteWidget, Group
from rest_framework import serializers
from mobili.helpers import haversine_distance


class LineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Line
        fields = (
            'id',
            'name',
            'mode',
        )

class DirectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Direction
        fields = (
            'id',
            'name',
        )

class LineStopSerializer(serializers.ModelSerializer):
    line = LineSerializer()
    direction = DirectionSerializer()
    times = serializers.SerializerMethodField()

    class Meta:
        model = LineStop
        fields = (
            'id',
            'point',
            'line',
            'direction',
            'times',
        )

    def get_times(self, widget):
        # Placeholder for WS updates
        return []

class StopSerializer(serializers.ModelSerializer):
    line_stops = LineStopSerializer(many=True)
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Stop
        fields = (
            'id',
            'itinisere_id',
            'name',
            'point',
            'line_stops',
            'distance',
        )

    def get_distance(self, stop):
        """
        Distance approximation
        """
        if stop.point is None:
            return 0
        try:
            location = self.context['view'].location
            d = haversine_distance(stop.point.tuple, location.point.tuple)
            return int(d * 1000)
        except Exception as e:
            print(e)
            return 0


class LocationLightSerializer(serializers.ModelSerializer):
    """
    Used by backend to manage line stops
    """

    # Nullable line_stops
    line_stops = serializers.PrimaryKeyRelatedField(queryset=LineStop.objects.all(), many=True, allow_null=True)

    class Meta:
        model = Location
        fields = (
            'id',
            'line_stops',
        )
        readonly_fields = (
            'id',
        )

class LocationSerializer(serializers.ModelSerializer):
    """
    Used by frontend to have full details on managed stops
    """
    # Nullable line_stops
    line_stops = LineStopSerializer(many=True)

    class Meta:
        model = Location
        fields = (
            'id',
            'line_stops',
        )

class WidgetSerializer(serializers.Serializer):
    """
    Cannot use a Modelserializer with an abstract class
    This serializer is just a base, see below for moar
    """
    id = serializers.UUIDField()
    type = serializers.SerializerMethodField()
    revision = serializers.SerializerMethodField()

    def get_type(self, widget):
        return widget.__class__.__name__

    def get_revision(self, widget):
        """
        Do NOT remove this
        This simplifies a lot the whole update process
        through websockets + vuejs : as we update on add_update
        the revision, the whole object gets evaluated again
        allowing us to add more fields !
        DEPRECATED ? to test
        """
        return 1

class ClockWidgetSerializer(WidgetSerializer):
    now = serializers.DateTimeField()

class NoteWidgetSerializer(WidgetSerializer):
    text = serializers.CharField()

    def update(self, widget, data):

        # Save on Db
        widget.text = data['text']
        widget.save()

        # Send update through ws
        widget.send_ws_update({
            'text' : widget.text,
        })
        return widget

class WeatherWidgetSerializer(WidgetSerializer):
    weather = serializers.CharField(source='get_weather')

class LocationWidgetSerializer(WidgetSerializer):
    location = LocationSerializer()

def get_widget_serializer(widget):
    """
    Find correct serializer for an instance
    """
    serializers = {
        ClockWidget : ClockWidgetSerializer,
        WeatherWidget : WeatherWidgetSerializer,
        NoteWidget : NoteWidgetSerializer,
        LocationWidget : LocationWidgetSerializer,
    }
    return serializers.get(widget.__class__, WidgetSerializer)

class WidgetsSerializer(serializers.ListSerializer):
    """
    This is where the magic happens:
    For each widget class, there is a mapped serializer
    """

    def __init__(self, *args, **kwargs):
        # Do not instanciante any "child"
        self.allow_empty = kwargs.pop('allow_empty', True)
        super(serializers.ListSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, widgets):
        def _serialize(widget):
            # Fetch the mapped serializer
            # Fallback to base serializer
            cls = get_widget_serializer(widget)
            return cls().to_representation(instance=widget)

        return [_serialize(w) for w in widgets]

class GroupSerializer(serializers.ModelSerializer):
    widgets = serializers.PrimaryKeyRelatedField(read_only=True, source='list_widgets', many=True)

    class Meta:
        model = Group
        fields = (
            'position',
            'vertical',
            'widgets',
            'groups',
        )

GroupSerializer._declared_fields['groups'] = GroupSerializer(many=True) # recursive !

class ScreenSerializer(serializers.ModelSerializer):

    groups = GroupSerializer(many=True, source='top_groups')

    widgets = WidgetsSerializer(source='all_widgets')

    class Meta:
        model = Screen
        fields = (
            'name',
            'slug',
            'ratio',
            'groups',
            'widgets',
        )

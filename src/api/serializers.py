from transport.models import Stop, LineStop, Line, Direction, City
from users.models import Location
from screen.models import Screen, ClockWidget, WeatherWidget, LocationWidget, NoteWidget, Group
from rest_framework import serializers
from rest_framework_gis.serializers import GeometrySerializerMethodField
from mobili.helpers import haversine_distance
import math


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = (
            'name',
        )

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

class StopLightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stop
        fields = (
            'id',
            'name',
        )

class LineStopSerializer(serializers.ModelSerializer):
    line = LineSerializer()
    direction = DirectionSerializer()
    stop = StopLightSerializer()

    class Meta:
        model = LineStop
        fields = (
            'id',
            'point',
            'line',
            'direction',
            'stop',
        )

class StopSerializer(serializers.ModelSerializer):
    line_stops = LineStopSerializer(many=True)
    approximate_distance = serializers.SerializerMethodField()

    class Meta:
        model = Stop
        fields = (
            'id',
            'itinisere_id',
            'name',
            'point',
            'line_stops',
            'approximate_distance',
        )

    def get_approximate_distance(self, stop):
        """
        Distance approximation
        """
        if stop.point is None:
            return 0
        try:
            location = self.context['view'].location
            d = haversine_distance(stop.point.tuple, location.point.tuple)
            return math.ceil(d * 100) * 10
        except Exception as e:
            print(e)
            return 0


class ScreenLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = (
            'name',
            'slug',
            'ratio',
        )


class LocationSerializer(serializers.ModelSerializer):
    """
    Used by frontend to have full details on managed stops
    """
    # Nullable line_stops
    line_stops = serializers.PrimaryKeyRelatedField(queryset=LineStop.objects.all(), many=True, allow_null=True)
    city = CitySerializer()
    screens = ScreenLightSerializer(many=True)

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'address',
            'city',
            'point',
            'line_stops',
            'screens',
        )
        readonly_fields = (
            'id',
            'name',
            'address',
            'city',
            'point',
            'screens',
        )


class WidgetSerializer(serializers.Serializer):
    """
    Cannot use a Modelserializer with an abstract class
    This serializer is just a base, see below for moar
    """
    id = serializers.UUIDField()
    type = serializers.SerializerMethodField()

    def get_type(self, widget):
        return widget.__class__.__name__

class ClockWidgetSerializer(WidgetSerializer):
    now = serializers.FloatField()

class NoteWidgetSerializer(WidgetSerializer):
    text = serializers.CharField()

    def update(self, widget, data):

        # Save on Db
        widget.text = data['text']
        widget.save()

        # Send update through ws
        widget.send_ws_update()

        return widget

class WeatherWidgetSerializer(WidgetSerializer):
    city = CitySerializer()

    def update(self, widget, data):

        # Save on Db
        #widget.save()

        # Send update through ws
        widget.send_ws_update()

        return widget

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

class DistanceSerializer(serializers.Serializer):
    distance = serializers.IntegerField()
    duration = serializers.IntegerField()
    geometry = GeometrySerializerMethodField()

    def get_geometry(self, data):
        return data['geometry']

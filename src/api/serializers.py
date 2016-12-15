from transport.models import Stop, LineStop, Line, Direction, City
from users.models import Location
from screen.models import Screen, ClockWidget, WeatherWidget, LocationWidget, NoteWidget, DisruptionWidget, Group
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework_gis.serializers import GeometrySerializerMethodField
from mobili.helpers import haversine_distance
import math

import logging
logger = logging.getLogger('api.serializers')


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = (
            'id',
            'name',
        )

class LineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Line
        fields = (
            'id',
            'name',
            'mode',
            'color_back',
            'color_front',
        )

class DirectionSerializer(serializers.ModelSerializer):
    disruptions = serializers.SerializerMethodField()

    class Meta:
        model = Direction
        fields = (
            'id',
            'name',
            'disruptions',
        )

    def get_disruptions(self, direction):
        # complex structure, not parsed
        return direction.get_disruptions(commercial=False)

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
    preview = serializers.HyperlinkedIdentityField(view_name='screen-preview', read_only=True, lookup_field='slug')

    class Meta:
        model = Screen
        fields = (
            'id',
            'name',
            'slug',
            'preview',
            'frontend_url',
        )


class LocationLightSerializer(serializers.ModelSerializer):
    """
    Used by backend to select new locations
    """
    city = CitySerializer()

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'address',
            'city',
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

    def update(self, widget, data):

        # Send update through ws
        widget.send_ws_update()

        return widget

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
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    def update(self, widget, data):
        # Update city
        city = data.get('city')
        save = False
        if city and city != widget.city:
            widget.city = city
            save = True

        # Send update through ws
        # it may fail due to cities missing positions
        try:
            widget.send_ws_update()
            if save:
                widget.save()
        except Exception as e:
            logger.error('Weather widget {} update failed: {}'.format(widget.id, e))
            raise APIException('Update failed')

        return widget

class LocationWidgetSerializer(WidgetSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    def update(self, widget, data):

        # Check location belongs to user
        location = data.get('location')
        if location and location != widget.location:
            if location.user != self.context['request'].user:
                raise APIException('Invalid location')
            widget.location = location
            widget.save()

        # Send update through ws
        widget.send_ws_update()

        return widget

class DisruptionWidgetSerializer(LocationWidgetSerializer):
    """
    Just keep track of a location, same as above
    """

def get_widget_serializer(widget):
    """
    Find correct serializer for an instance
    """
    # TODO: move in central controller
    serializers = {
        ClockWidget : ClockWidgetSerializer,
        WeatherWidget : WeatherWidgetSerializer,
        NoteWidget : NoteWidgetSerializer,
        LocationWidget : LocationWidgetSerializer,
        DisruptionWidget : DisruptionWidgetSerializer,
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
            'id',
            'position',
            'vertical',
            'widgets',
            'groups',
        )

GroupSerializer._declared_fields['groups'] = GroupSerializer(many=True) # recursive !

class ScreenSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    groups = GroupSerializer(many=True, source='top_groups')

    widgets = WidgetsSerializer(source='all_widgets')

    class Meta:
        model = Screen
        fields = (
            'name',
            'slug',
            'frontend_url',
            'style',
            'admin',
            'groups',
            'widgets',
        )

    def get_admin(self, screen):
        # Used to show admin actions
        return screen.user.is_admin

class DistanceSerializer(serializers.Serializer):
    distance = serializers.IntegerField()
    duration = serializers.IntegerField()
    geometry = GeometrySerializerMethodField()

    def get_geometry(self, data):
        return data['geometry']


class WidgetCreationSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    widget_type = serializers.CharField()

class ScreenCreationSerializer(serializers.Serializer):
    template = serializers.PrimaryKeyRelatedField(queryset=Screen.objects.filter(is_template=True))
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    name = serializers.CharField()

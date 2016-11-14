from transport.models import Stop, LineStop, Line, Direction
from users.models import Location
from screen.models import Screen
from rest_framework import serializers
from mobili.helpers import haversine_distance
import json


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

    class Meta:
        model = LineStop
        fields = (
            'id',
            'point',
            'line',
            'direction',
        )

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


class LocationSerializer(serializers.ModelSerializer):
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

class WidgetSerializer(serializers.Serializer):
    """
    Cannot use a Modelserializer with an abstract class
    """
    id = serializers.IntegerField()
    type = serializers.SerializerMethodField()
    top = serializers.IntegerField()
    left = serializers.IntegerField()
    bottom = serializers.IntegerField()
    right = serializers.IntegerField()
    payload = serializers.SerializerMethodField()

    def get_type(self, widget):
        return widget.__class__.__name__

    def get_payload(self, widget):
        return widget.build_payload()

class ScreenSerializer(serializers.ModelSerializer):

    widgets = WidgetSerializer(source='list_widgets', many=True)

    class Meta:
        model = Screen
        fields = (
            'slug',
            'ratio',
            'widgets',
        )

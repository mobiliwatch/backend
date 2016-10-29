from transport.models import Stop, LineStop, Line, Direction
from rest_framework import serializers

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

    class Meta:
        model = Stop
        fields = (
            'id',
            'itinisere_id',
            'name',
            'line_stops',
        )

from rest_framework import serializers


class OHLCSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    open = serializers.FloatField()
    high = serializers.FloatField()
    low = serializers.FloatField()
    close = serializers.FloatField()
    volume = serializers.IntegerField(allow_null=True)

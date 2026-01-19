from rest_framework import serializers

__all__ = ['SimpleSerializer']

class SimpleSerializer(serializers.ModelSerializer):
    """Serializer meant to output basic data"""

    class Meta:
        model = None
        fields = "__all__"
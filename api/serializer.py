from rest_framework import serializers

class VariableValidationSerializer(serializers.Serializer):
    # Safely maps frontend camelCase to backend readable fields
    varName = serializers.CharField()
    dimension = serializers.CharField()
    repeatingVar = serializers.BooleanField()
    M = serializers.FloatField()
    L = serializers.FloatField()
    T = serializers.FloatField()
    Theta = serializers.FloatField()

class PiGroupPayloadSerializer(serializers.Serializer):
    # Validates the two incoming arrays from your frontend
    repeating = VariableValidationSerializer(many=True)
    nonRepeating = VariableValidationSerializer(many=True)
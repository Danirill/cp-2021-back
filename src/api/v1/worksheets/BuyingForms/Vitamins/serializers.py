from rest_framework import serializers
class VitaminsFormSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.IntegerField(),
                                   required=True,
                                   allow_null=True)
    name = serializers.CharField(required=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)




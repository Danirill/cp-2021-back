from rest_framework import serializers

from api.v1.images.models import Image


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Image
        fields = ['id','image_url', 'uuid']

    def get_image_url(self, image):
        request = self.context.get('request')
        photo_url = image.image.url
        return request.build_absolute_uri(photo_url)
from rest_framework import serializers

from api.v1.videos.models import Video


class VideoSerializer(serializers.ModelSerializer):
    video_file = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = ['id','video_file', 'video_url']

    def get_video_file(self, video):
        request = self.context.get('request')
        if video.video_file:
            video_file = video.video_file.url
            return request.build_absolute_uri(video_file)
        return None

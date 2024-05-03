from django.db import models


class Channel(models.Model):
    name = models.CharField(max_length=80, blank=True)
    channel_id = models.CharField(max_length=36, unique=True)


class VideoDetail(models.Model):
    video_id = models.CharField(max_length=16)
    video_name = models.CharField(max_length=80, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    season = models.IntegerField(null=False, blank=False) 
    episode = models.IntegerField(null=False, blank=False)
    link = models.TextField(blank=True)
    convert_link = models.TextField(blank=True)

    class Meta:
        unique_together = (('channel', 'video_id'),)


class ConvertedVideo(models.Model):
    video = models.OneToOneField(VideoDetail, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    link = models.TextField(blank=True)



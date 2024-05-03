from django.db import models

from download.models import VideoDetail, Channel

# Create your models here.
class UploadedVideo(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    uploaded_youtube_id = models.CharField(max_length=11)
    video = models.OneToOneField(VideoDetail, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
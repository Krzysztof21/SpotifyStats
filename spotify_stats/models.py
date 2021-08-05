from django.db import models


# Create your models here.
class Track(models.Model):
    track_name = models.TextField(blank=True, null=True)
    album_name = models.TextField(blank=True, null=True)
    artist_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'track'

    def __str__(self):
        return self.track_name


class Stream(models.Model):
    end_time = models.DateTimeField()
    ms_played = models.IntegerField()
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'stream'

    def __str__(self):
        return str(self.end_time)

from django.db import models
from django.db.models import Count, Sum

from datetime import datetime, timedelta, timezone
from .utils import milliseconds_to_hh_mm_ss


class StreamManager(models.Manager):
    def get_total_streams(self, track_id):
        return self._get_streams_for_track(track_id).aggregate(Count('id'))['id__count']

    def get_total_time_listened(self, track_id):
        time_tuple = milliseconds_to_hh_mm_ss(
            self._get_streams_for_track(track_id).aggregate(Sum('ms_played'))['ms_played__sum'])
        return f'{time_tuple[0]}:{time_tuple[1]}:{time_tuple[2]}'

    def get_number_last_week_streams(self, track_id):
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M%z')
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d %H:%M%z')
        streams = self._get_streams_for_track(track_id).filter(end_time__gte=week_ago, end_time__lte=today)
        return streams.aggregate(Count('id'))['id__count']

    def _get_streams_for_track(self, track_id):
        return self.filter(track_id=track_id)


class Track(models.Model):
    track_name = models.TextField(blank=True, null=True)
    album_name = models.TextField(blank=True, null=True)
    artist_name = models.TextField(blank=True, null=True)
    track_length = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'track'

    def __str__(self):
        return self.track_name


class Stream(models.Model):
    objects = StreamManager()

    end_time = models.DateTimeField()
    ms_played = models.IntegerField()
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'stream'

    def __str__(self):
        return str(self.track)





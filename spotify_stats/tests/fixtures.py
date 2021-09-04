import pytest
from datetime import datetime, timezone, timedelta

from spotify_stats.models import Track, Stream


@pytest.fixture(scope='function')
def db_test_version(django_db_blocker):
    with django_db_blocker.unblock():
        date_last_week = (datetime.now(timezone.utc) - timedelta(days=3)).strftime('%Y-%m-%d %H:%M%z')
        tracks = [
            Track(0, 'Ethnicolor - Remastered', 'Zoolook', 'Jean-Michel Jarre'),
            Track(1, 'Children of the Moon', 'Eye In The Sky (Expanded Edition)', 'The Alan Parsons Project'),
            Track(2, 'Johnny and Mary', "It's Album Time", 'Todd Terje'),
            Track(3, 'Love Buzz', 'At Home', 'Shocking Blue')
        ]
        Track.objects.bulk_create(tracks)
        streams = [
            Stream(end_time='2020-01-16 23:30+01:00', ms_played='300000', track=tracks[0]),
            Stream(end_time='2020-02-16 23:30+01:00', ms_played='300000', track=tracks[0]),
            Stream(end_time='2020-03-16 23:30+01:00', ms_played='300000', track=tracks[0]),
            Stream(end_time=date_last_week,           ms_played='300000', track=tracks[0]),
            Stream(end_time='2020-01-17 23:30+01:00', ms_played='300000', track=tracks[1]),
            Stream(end_time='2020-02-17 23:30+01:00', ms_played='300000', track=tracks[1]),
            Stream(end_time='2020-03-17 23:30+01:00', ms_played='300000', track=tracks[1]),
            Stream(end_time='2020-01-18 23:30+01:00', ms_played='300000', track=tracks[2]),
            Stream(end_time='2020-02-18 23:30+01:00', ms_played='300000', track=tracks[2]),
            Stream(end_time='2020-02-19 23:30+01:00', ms_played='10000', track=tracks[3]),
            Stream(end_time='2020-02-20 23:30+01:00', ms_played='10000', track=tracks[3]),
            Stream(end_time='2020-02-21 23:30+01:00', ms_played='10000', track=tracks[3]),
            Stream(end_time='2020-02-22 23:30+01:00', ms_played='10000', track=tracks[3]),
            Stream(end_time='2020-02-23 23:30+01:00', ms_played='10000', track=tracks[3])
        ]
        Stream.objects.bulk_create(streams)

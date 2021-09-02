import pytest
from datetime import datetime, timedelta, timezone

from django.urls import reverse

from spotify_stats.models import Stream, Track


@pytest.mark.django_db
class TestBasicStats:
    @pytest.fixture
    def db_test_version(self, db):
        date_last_week = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d %H:%M%z')
        track = Track.objects.create(
            track_name='Ethnicolor - Remastered', album_name='Zoolook', artist_name='Jean-Michel Jarre'
        )
        track.save()
        data = [
            Stream(end_time='2020-01-16 23:30+01:00', ms_played='300000', track=track),
            Stream(end_time='2020-02-16 23:30+01:00', ms_played='300000', track=track),
            Stream(end_time='2020-03-16 23:30+01:00', ms_played='300000', track=track),
            Stream(end_time=date_last_week,     ms_played='300000', track=track)
        ]
        Stream.objects.bulk_create(data)

    def test_existing(self, db_test_version, client):
        response = client.get(reverse('spotify_stats:basic_stats', args=[1]))
        assert response.status_code == 200
        response_content = response.content.decode()
        assert "Ethnicolor - Remastered" in response_content
        assert "Jean-Michel Jarre" in response_content
        assert "4" in response_content
        assert "0:20:00" in response_content
        assert "1" in response_content

    def test_nonexistent(self, client):
        response = client.get(reverse('spotify_stats:basic_stats', args=[3]))
        assert response.status_code == 404
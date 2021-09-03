import pytest
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone

from django.urls import reverse
from django.test.client import RequestFactory

from spotify_stats.models import Stream, Track
from spotify_stats.views import *


@pytest.fixture(scope="module")
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
            Stream(end_time='2020-02-19 23:30+01:00', ms_played='300000', track=tracks[3])
        ]
        Stream.objects.bulk_create(streams)


@pytest.mark.django_db
class TestDetailViews:

    @pytest.mark.parametrize('track_or_stream, id, expected', [
        pytest.param('track', 1, 200, id='track_1'),
        pytest.param('track', 100, 404, id='track_100'),
        pytest.param('track', 10000000, 404, id='track_1000000'),
        pytest.param('stream', 1, 200, id='stream_1'),
        pytest.param('stream', 100, 404, id='stream_100'),
        pytest.param('stream', 10000000, 404, id='stream_1000000')
    ])
    def test_existence(self, db_test_version, client, track_or_stream, id, expected):
        response = client.get(reverse(f'spotify_stats:{track_or_stream}_detail', args=[id]))
        assert response.status_code == expected

    @pytest.mark.parametrize('track_or_stream, id, expected', [
        pytest.param('track', 2, ('Johnny and Mary', "It&#x27;s Album Time", 'Todd Terje'), id='track_1'),
        pytest.param('stream', 1, ('Jan. 16, 2020', '300000', '0'), id='stream_1'),
    ])
    def test_response(self, db_test_version, client, track_or_stream, id, expected):
        response = client.get(reverse(f'spotify_stats:{track_or_stream}_detail', args=[id]))
        assert response.status_code == 200
        response_content = response.content.decode()
        for exp in expected:
            assert exp in response_content


@pytest.mark.django_db
class TestMostListened:

    def test_most_listened(self, db_test_version, client):
        payload = urlencode({
            'start_time': '2020-01-01',
            'end_time': '2021-09-01',
            'include_podcasts': 0,
            'limit': 5,
            'order': 'total_time'
        })
        base_url = reverse('spotify_stats:most_listened')
        response = client.get('{}?{}'.format(base_url, payload))
        assert response.status_code == 200
        response_content = response.content.decode()
        # TODO: asserts with html content


@pytest.mark.django_db
class TestBasicStats:

    def test_existing(self, db_test_version, client):
        response = client.get(reverse('spotify_stats:basic_stats', args=[0]))
        assert response.status_code == 200
        response_content = response.content.decode()
        assert "Ethnicolor - Remastered" in response_content
        assert "Jean-Michel Jarre" in response_content
        assert "4" in response_content
        assert "0:20:00" in response_content
        assert "1" in response_content

    def test_nonexistent(self, client):
        response = client.get(reverse('spotify_stats:basic_stats', args=[400]))
        assert response.status_code == 404

import pytest
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import re

from django.urls import reverse
from django.test.client import RequestFactory

from spotify_stats.models import Stream, Track
from spotify_stats.views import *

from spotify_stats.tests.fixtures import db_test_version


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

    end_time = datetime.today().strftime('%Y-%m-%d')

    @pytest.mark.parametrize('query, expected', [
        pytest.param({'start_time': '2020-01-01', 'end_time': end_time, 'include_podcasts': 0, 'limit': 5,
                      'order': 'total_time'},
                     ('>1<.{4}\n.*0/>Ethnicolor - Remastered',
                      'Ethnicolor - Remastered.*\n.*\n.*0:20:00'),
                     id='total_time'),
        pytest.param({'start_time': '2020-01-01', 'end_time': end_time, 'include_podcasts': 0, 'limit': 5,
                      'order': 'no_streams'},
                     ('>1<.{4}\n.*3/>Love Buzz',
                      'Love Buzz.*\n.*\n.*0:00:50'),
                     id='no_streams'),
    ])
    def test_most_listened(self, db_test_version, client, query, expected):
        payload = urlencode(query)
        base_url = reverse('spotify_stats:most_listened')
        response = client.get('{}?{}'.format(base_url, payload))
        assert response.status_code == 200
        response_content = response.content.decode()
        pattern0 = re.compile(expected[0])
        assert re.search(pattern0, response_content) is not None
        pattern1 = re.compile(expected[1])
        assert re.search(pattern1, response_content) is not None
        assert '0:20:00' in response_content


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

import pytest

from django.urls import reverse

from spotify_stats.models import Stream, Track
from spotify_stats.tests.fixtures import db_test_version


@pytest.mark.django_db
class TestModels:

    def test_existing_stream(self, client, db_test_version):
        response = client.get(reverse('spotify_stats:stream_detail', args=[1]))
        response_content = response.content.decode()
        assert response.status_code == 200
        assert "tracks/1/" in response_content
        assert "300000" in response_content
        assert "Jan. 16, 2020" in response_content

    def test_nonexistent_stream(self, client, db_test_version):
        response = client.get(reverse('spotify_stats:stream_detail', args=[100]))
        assert response.status_code == 404

    def test_stream_manager(self, client, db_test_version):
        assert Stream.objects.get_total_streams(0) == 4
        assert Stream.objects.get_total_time_listened(0) == '0:20:00'
        assert Stream.objects.get_number_last_week_streams(0) == 1

        assert Stream.objects.get_total_streams(3) == 5
        assert Stream.objects.get_total_time_listened(3) == '0:00:50'
        assert Stream.objects.get_number_last_week_streams(3) == 0

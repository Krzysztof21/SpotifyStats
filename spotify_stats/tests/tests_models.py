import pytest

from django.urls import reverse

from spotify_stats.models import Stream, Track


class TestModels:

    @pytest.fixture
    def track_1(self, db):
        return Track.objects.create(
                track_name='Ethnicolor - Remastered',
                album_name='Zoolook',
                artist_name='Jean-Michel Jarre'
            )

    @pytest.fixture
    def stream_1(self, db, track_1):
        return Stream.objects.create(
            end_time='2020-01-16 23:30+01:00',
            ms_played='38089',
            track=track_1
        )

    def test_existing_stream(self, client, db, stream_1):
        response = client.get(reverse('spotify_stats:detail', args=[1]))
        response_content = response.content.decode()
        assert response.status_code == 200
        assert "Ethnicolor - Remastered" in response_content
        assert "Jean-Michel Jarre" in response_content
        assert "Jan. 16, 2020" in response_content

    def test_nonexistent_stream(self, client, db):
        response = client.get(reverse('spotify_stats:detail', args=[2]))
        assert response.status_code == 404
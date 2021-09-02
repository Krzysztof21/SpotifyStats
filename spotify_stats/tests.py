import pytest
from datetime import datetime, timedelta, timezone

from django.urls import reverse

from .utils import milliseconds_to_hh_mm_ss
from .models import Stream, Track


class TestMillisecondsConverter:

    @pytest.mark.parametrize('milliseconds, expected', [
        pytest.param(5345, ('0', '00', '05'), id='single_digit_sec'),
        pytest.param(85345, ('0', '01', '25'), id='double_digit_sec'),
        pytest.param(125345, ('0', '02', '05'), id='single_digit_min'),
        pytest.param(5005345, ('1', '23', '25'), id='double_digit_min')
    ])
    def test_conversion(self, milliseconds, expected):
        assert milliseconds_to_hh_mm_ss(milliseconds) == expected

    def test_negative_number_exception(self):
        with pytest.raises(ValueError):
            milliseconds_to_hh_mm_ss(-100)


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
        response = client.get(reverse('spotify_stats:stream_detail', args=[1]))
        response_content = response.content.decode()
        assert response.status_code == 200
        assert "38089" in response_content
        assert "Jan. 16, 2020" in response_content

    def test_nonexistent_stream(self, client, db):
        response = client.get(reverse('spotify_stats:stream_detail', args=[2]))
        assert response.status_code == 404


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

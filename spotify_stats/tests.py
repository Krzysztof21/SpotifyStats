import pytest

from django.urls import reverse

from .utils import milliseconds_to_hh_mm_ss
from .models import Stream, Track

from django.urls.exceptions import NoReverseMatch


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
            end_time='2020-01-16 23:30',
            ms_played='38089',
            track=track_1
        )

    def test_existing_stream(self, client, db, stream_1):
        response = client.get(reverse('spotify_stats:detail', args=[1]))
        response_content = str(response.content)
        assert response.status_code == 200
        assert "Ethnicolor - Remastered" in response_content
        assert "Jean-Michel Jarre" in response_content
        assert "Jan. 16, 2020" in response_content

    def test_nonexistent_stream(self, client, db):
        response = client.get(reverse('spotify_stats:detail', args=[2]))
        assert response.status_code == 404

    # TODO: maybe it should not be in this class
    def test_wrong_url(self, client):
        with pytest.raises(NoReverseMatch):
            client.get(reverse('spotify_stats:detail', args=[-2]))

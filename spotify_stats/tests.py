import unittest
from parameterized import parameterized

from django.test import TestCase
from django.urls import reverse

from .utils import milliseconds_to_hh_mm_ss
from .models import Stream, Track


class UtilsTests(TestCase):
    @parameterized.expand([
        ('single_digit_sec', 5345, ('0', '00', '05')),
        ('double_digit_sec', 85345, ('0', '01', '25')),
        ('single_digit_min', 125345, ('0', '02', '05')),
        ('double_digit_min', 5005345, ('1', '23', '25'))
    ])
    def test_milliseconds_to_hh_mm_ss_conversion(self, name, milliseconds, expected):
        self.assertEqual(milliseconds_to_hh_mm_ss(milliseconds), expected)

    def test_milliseconds_to_hh_mm_ss_exception(self):
        self.assertRaises(ValueError, milliseconds_to_hh_mm_ss, -100)


class DetailTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        track = Track.objects.create(
            track_name='Ethnicolor - Remastered',
            album_name='Zoolook',
            artist_name='Jean-Michel Jarre'
        )
        Stream.objects.create(
            end_time='2020-01-16 23:30',
            ms_played='38089',
            track=track
        )

    def test_existing_stream(self):
        response = self.client.get(reverse('spotify_stats:detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ethnicolor - Remastered")
        self.assertContains(response, 'Jean-Michel Jarre')
        self.assertContains(response, 'Jan. 16, 2020')

    def test_nonexistent_stream(self):
        response = self.client.get(reverse('spotify_stats:detail', args=[2]))
        self.assertEqual(response.status_code, 404)

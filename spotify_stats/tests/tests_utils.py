import pytest

from spotify_stats.utils import milliseconds_to_hh_mm_ss


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
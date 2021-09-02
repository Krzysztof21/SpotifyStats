import pytest

from spotify_stats.forms import DateForm


class TestDateForm:

    @staticmethod
    def values_for_test(change_dict=None):
        correct_data = {
            "start_date": "2021-08-01",
            "end_date": "2021-08-02",
            "include_podcasts": True,
            "limit": 5,
            "order": 'no_streams'
        }
        if change_dict is None:
            return correct_data
        correct_data.update(change_dict)
        return correct_data

    @pytest.mark.parametrize('altered_data, expected', [
        pytest.param(None, True, id='correct_data'),
        pytest.param({'start_date': "2021-08-02", 'end_date': "2021-08-01" }, False, id='wrong_date_order'),
        pytest.param({'start_date': "2021-10-02", 'end_date': "2021-08-01"}, False, id='start_date_future'),
        pytest.param({'end_date': "2021-10-01"}, False, id='end_date_future')
    ])
    def test_date_validation(self, altered_data, expected):
        form = DateForm(data=self.values_for_test(altered_data))
        assert form.is_valid() is expected

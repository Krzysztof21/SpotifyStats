import datetime as dt

from django.core.exceptions import ValidationError
from django import forms


class DateForm(forms.Form):
    display_choices = [
        ('list', 'List'),
        ('chart', 'Chart')
    ]
    display = forms.CharField(label='Choose display', widget=forms.Select(choices=display_choices))
    start_date = forms.DateTimeField(label='Start date')
    end_date = forms.DateTimeField(label='End date')
    include_podcasts = forms.BooleanField(widget=forms.CheckboxInput(), label='Include podcasts', required=False)
    limit = forms.IntegerField(min_value=5, initial=5)
    order_choices = [
        ('total_time', 'Total time listened'),
        ('no_streams', 'Number of streams')
    ]
    order = forms.CharField(label='Choose order', widget=forms.Select(choices=order_choices))

    def clean_start_date(self):
        return self.check_date_before_present(self.cleaned_data['start_date'])

    def clean_end_date(self):
        return self.check_date_before_present(self.cleaned_data['end_date'])

    def clean(self):
        cleaned_data = super().clean()
        if any(self.errors):
            return self.errors
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if end_date < start_date:
            raise forms.ValidationError("Start date must be earlier than end date")

    @staticmethod
    def check_date_before_present(date):
        now = dt.datetime.now(dt.timezone.utc).astimezone()
        if date > now:
            raise forms.ValidationError("Date must be in the past")
        return date


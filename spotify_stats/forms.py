from django import forms


class DateForm(forms.Form):
    start_date = forms.DateTimeField(label='Start date')
    end_date = forms.DateTimeField(label='End date')
    include_podcasts = forms.BooleanField(widget=forms.CheckboxInput(), label='Include podcasts', required=False)
    limit = forms.IntegerField(min_value=5, initial=5)
    order_choices = [
        ('total_time', 'Total time listened'),
        ('no_streams', 'Number of streams')
    ]
    order = forms.CharField(label='Choose order', widget=forms.Select(choices=order_choices))


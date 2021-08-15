from django import forms


class DateForm(forms.Form):
    start_date = forms.DateTimeField(label='Start date')
    end_date = forms.DateTimeField(label='End date')
    include_podcasts = forms.BooleanField(widget=forms.CheckboxInput(), label='Include podcasts')


from django import forms


class DateForm(forms.Form):
    start_date = forms.DateTimeField(label='Start date')
    end_date = forms.DateTimeField(label='End date')


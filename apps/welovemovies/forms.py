
from django import forms


class ScheduleViewingForm(forms.Form):
    scheduled_for = forms.DateField(input_formats=['%b %d, %Y'], required=False)

from django import forms

from welovemovies.models import Viewing, Schedule


class ScheduleViewingForm(forms.Form):
    scheduled_for = forms.DateField(input_formats=['%b %d, %Y'], required=False)


class RecordViewingForm(forms.ModelForm):
    summary = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Viewing
        fields = ('viewed_on', 'rating', 'summary')


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('monday','tuesday','wednesday','thursday','friday','saturday','sunday')


from django import forms

from .models import Event


class EventCreateForm(forms.ModelForm):
    time_start = forms.DateTimeField(widget=forms.DateTimeInput)
    time_end = forms.DateTimeField(widget=forms.DateTimeInput)

    class Meta:
        model = Event
        exclude = ("date_created", "yes", "no", "maybe", "creator", "group", "is_started")


class PollForms(forms.Form):
    title = forms.CharField(max_length=90, required=True, help_text="Enter the Question ?")
    start_date = forms.DateTimeField(required=True)
    stop_date = forms.DateTimeField(required=True)
    poll_option1 = forms.CharField(max_length=50, required=True)
    poll_option2 = forms.CharField(max_length=50, required=True)
    poll_option3 = forms.CharField(max_length=50, )
    poll_option4 = forms.CharField(max_length=50)


from django import forms



from .models import Event


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ("date_created", "yes", "no", "maybe", "creator", "group")


class PollForms(forms.Form):
    title = forms.CharField(max_length=90, required=True)
    start_date = forms.DateTimeField(required=True)
    stop_date = forms.DateTimeField(required=True)
    polls_option1 = forms.CharField(max_length=50, required=True)
    polls_option2 = forms.CharField(max_length=50, required=True)
    polls_option3 = forms.CharField(max_length=50,)
    polls_option4 = forms.CharField(max_length=50)

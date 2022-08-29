from django import form

from .models import Groups


class GroupCreateForm(form.ModelForm):
    class Meta:
        model = Groups
        exclude = ("owner", "date_created", "is_closed", "is_active")
        
        
from django import forms

from .models import Groups, Posts
from django_ckeditor_5.widgets import CKEditor5Widget


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Groups
        exclude = ("owner", "date_created",
                   "is_active", 'picture')


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].required = False

    def clean(self):
        print(super().clean)

    class Meta:
        model = Posts
        fields = ("body",)
        widgets = {
            "body": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "value": f"body"}, config_name="extends"
            )
        }

from dataclasses import field
from django import forms

from .models import Group, Posts, Comments, Replies
from django_ckeditor_5.widgets import CKEditor5Widget


class GroupCreateForm(forms.ModelForm):
    name_of_group = forms.CharField(widget=forms.TextInput
                            (attrs={'placeholder': f'Group Name', 'class':
                                    'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[5px] bg-[#FBFBFB] outline-none '}))
    title = forms.CharField(widget=forms.TextInput
                            (attrs={'placeholder': f'Group Title', 'class':
                                    'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[15px] bg-[#FBFBFB] outline-none '}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': f'Group Description', 'class':
                                    'border rounded-[10px] pl-[20px] mt-[15px] bg-[#FBFBFB] outline-none ', 'cols': 70, 'rows': 10}))

    class Meta:
        model = Group
        exclude = ("owner", "date_created",
                   "is_active", 'picture')


class PostForm(forms.ModelForm):
    
    title = forms.CharField(widget=forms.TextInput
                            (attrs={'placeholder': f'Group Title', 'class':
                                    'border rounded-[10px] w-[483px] h-[43px] pl-[20px] mt-[15px] bg-[#FBFBFB] outline-none '}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].required = False

    def clean(self):
        print(super().clean)

    class Meta:
        model = Posts
        fields = ("title","body",)
        widgets = {
            "body": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5 w-1/2", "value": f"body"}, config_name="extends"
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ("content",)
        

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Replies
        fields = ("content",) 
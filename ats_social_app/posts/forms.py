from django import forms
from .models import Comments, Post, Reply


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'image', 'tags', 'likes']


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']
        widget = {
            'comment': forms.Textarea(attrs={'class': 'md-textarea form-control',
                                             'placeholder': 'comment here ...',
                                      'row': '4'}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['reply']
        widget = {
            'reply': forms.Textarea(attrs={'class': 'md-textarea form-control',
                                           'placeholder': 'comment here ...',
                                           'row': '4'}),
        }

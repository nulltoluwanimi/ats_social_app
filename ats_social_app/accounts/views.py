from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewCommentForm, NewPostForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json


# Create your views here.
from .forms import NewCommentForm, NewPostForm
from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView, DetailView)

from django.contrib.auth.models import User
from .models import Post, Comments


def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post-details', args=[str('pk')]))


class PostListView(ListView):
    model = Post
    template_name = 'accounts/home.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostDetailsView(DetailView):
    model = Post
    template_name = "accounts/post_detail.html"
    form = NewCommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_comments = Comments.objects.all().filter(post=self.object.id)
        post_comment_counts = post_comments.count()
        post_is_liked = Post.objects.filter(likes=self.object.id)
        is_liked_counts = post_is_liked.count()
        context["form"] = self.form
        context["post_is_liked"] = post_is_liked
        context.update({
                    'form': self.form,
                    'post_comments': post_comments,
                    'post_comment_counts': post_comment_counts,
                    'post_is_liked': post_is_liked,
                    'is_liked_counts': is_liked_counts,
                    })
        return context

        def post(self, request, *args, **kwargs):
            form = NewCommentForm(request.POST)
            post = self.get_object()
            if form.is_valid():
                form = NewCommentForm.save(commit=False)
                form.instance.user = request.user
                form.instance.post = post
                try:
                    parent = NewCommentForm.cleaned_data['parent']
                    form.instance.parent = parent
                except parent.DoesNotExist:
                    parent = None
                form = NewCommentForm.save()
                return redirect(reverse("post-detail", kwargs={'pk': post.id}))


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = NewPostForm
    template_name = 'accounts/add_post.html'
    success_url = reverse_lazy('home')
    # permission_required = ('account.can_create',)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['description', 'pic', 'tags']
    template_name = 'accounts/create_post.html'

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user_name:
            return True
        else:
            return False


class DeletePost(DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    template_name = 'account/delete_post.html'

    def post_delete(request, pk):
        post = Post.objects.get(Post, pk=pk)
        if request.user == post.user_name:
            Post.objects.get(pk=pk).delete()
        return redirect('home')

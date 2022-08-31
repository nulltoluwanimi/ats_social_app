from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
	path('', views.PostListView.as_view(), name='home'),
	path('post/new', views.CreatePostView.as_view(), name='create-post'),
	path('post/<int:pk>/detail', views.PostDetailsView.as_view(), name='post-detail'),
	path('post/<int:pk>/update', views.PostUpdateView.as_view(), name='post-update'),
	path('post/<int:pk>/delete', views.post_delete, name='delete-post'),
	path('like/<int:pk', views.LikeView, name='like_post'),
	path('search_posts', views.search_posts, name='search-posts'),
]

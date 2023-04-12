
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from .registration import CreateUserView
from links.views import RemoveUpvoteView,UpvoteSubmissionView,HomeView,NewSubmissionView,SubmissionDetailView, NewCommentView, NewCommentReplyView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include('django.contrib.auth.urls')),
    path("", HomeView.as_view(), name='home'),
    path("accounts/register/", CreateUserView.as_view(), name='register'),

    path("new-submission/", NewSubmissionView.as_view(), name='new-submission'),
    path("submission/<int:pk>/", SubmissionDetailView.as_view(), name='submission-detail'),
    path("new-comment/", NewCommentView.as_view(), name='new-comment'),
    path("new-comment-reply/", NewCommentReplyView.as_view(), name='new-comment-reply'),
    path('upvote/<int:link_pk>/', UpvoteSubmissionView.as_view(), name='upvote'),
    path('upvote/<int:link_pk>/remove', RemoveUpvoteView.as_view(), name='remove-vote'),
]

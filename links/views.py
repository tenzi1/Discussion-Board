from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, TemplateView, View
from .models import Link, Comment
from .forms import CommentModelForm

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        submissions = Link.objects.all()
        for submission in submissions:
            num_votes = submission.upvotes.count()
            num_comments = submission.comment_set.count()
            date_diff = now - submission.submitted_on
            number_of_day_since_submission = date_diff.days
            submission.rank = num_votes + num_comments - number_of_day_since_submission
        sorted_submissions = sorted(submissions, key=lambda x:x.rank, reverse=True)
        context['submissions'] = sorted_submissions
        return context 

    
class NewSubmissionView(CreateView):
    model = Link
    fields = ('title', 'url')
    template_name = 'new_submission.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NewSubmissionView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        new_link = form.save(commit=False)
        new_link.submitted_by = self.request.user
        new_link.save()
        self.object = new_link
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self) -> str:
        return reverse('submission-detail', kwargs={'pk':self.object.pk})
    

class SubmissionDetailView(DetailView):
    model = Link
    template_name = 'submission_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SubmissionDetailView, self).get_context_data(**kwargs)
        submission_comments = Comment.objects.filter(commented_on=self.get_object(), in_reply_to__isnull=True)
        context['comments'] = submission_comments
        context['comment_form'] = CommentModelForm(initial={'link_pk': self.get_object().pk})
        return context


class NewCommentView(CreateView):
    form_class = CommentModelForm
    http_method_names = ('post',)
    template_name = 'comment.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NewCommentView, self).dispatch(request,*args, **kwargs)
    
    def form_valid(self, form):
        parent_link = Link.objects.get(pk=form.cleaned_data['link_pk'])
        new_comment = form.save(commit=False)
        new_comment.commented_on = parent_link
        new_comment.commented_by = self.request.user
        new_comment.save()
        return HttpResponseRedirect(reverse('submission-detail', kwargs={'pk':parent_link.pk}))
    
    def get_initial(self):
        initial_data =  super().get_initial()
        initial_data['link_pk'] = self.request.GET['link_pk']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = Link.objects.get(pk=self.request.GET['link_pk'])
        return context
    

class NewCommentReplyView(CreateView):
    form_class = CommentModelForm
    template_name = 'comment_reply.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_comment'] = Comment.objects.get(pk=self.request.GET['parent_comment_pk'])
        return context
    
    def get_initial(self):
        initial_data = super().get_initial()
        link_pk = self.request.GET['link_pk']
        initial_data['link_pk'] = link_pk
        parent_comment_pk = self.request.GET['parent_comment_pk']
        initial_data['parent_comment_pk'] = parent_comment_pk
        return initial_data
    
    def form_valid(self, form):
        parent_link = Link.objects.get(pk=form.cleaned_data['link_pk'])
        parent_comment = Comment.objects.get(pk=form.cleaned_data['parent_comment_pk'])
        new_comment = form.save(commit=False)
        new_comment.commented_on = parent_link
        new_comment.in_reply_to = parent_comment
        new_comment.commented_by = self.request.user
        new_comment.save()
        return HttpResponseRedirect(reverse('submission-detail', kwargs={'pk':parent_link.pk}))
    

class UpvoteSubmissionView(View):
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, link_pk, **kwargs):
        link = Link.objects.get(pk=link_pk)
        link.upvotes.add(request.user)
        return HttpResponseRedirect(reverse('home'))



class RemoveUpvoteView(View):

    def get(self, request, link_pk, **kwargs):
        link = Link.objects.get(pk=link_pk)
        link.upvotes.remove(request.user)
        return HttpResponseRedirect(reverse('home'))
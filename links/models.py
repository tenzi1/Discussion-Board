from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Link(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upvotes = models.ManyToManyField(User, related_name='votes')
    submitted_on = models.DateTimeField(auto_now_add=True, editable=False)


class Comment(models.Model):
    body = models.TextField()
    commented_on = models.ForeignKey(Link, on_delete=models.CASCADE)
    in_reply_to = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)

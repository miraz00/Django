from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", symmetrical=False, related_name="followers", null=True, blank=True)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=5124)
    liked_by = models.ManyToManyField(User, related_name="likes", null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)


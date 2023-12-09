from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import *


class UserFollowing(TestCase):
    def setUp(self):
        ronaldo = User.objects.create(username="ronaldo")
        messi = User.objects.create(username="messi")
        neymar = User.objects.create(username="neymar")

        ronaldo.following.add(neymar)
        messi.following.add(neymar)

    def test_followers(self):
        neymar = User.objects.get(username="neymar")
        self.assertEqual(neymar.followers.count(), 2)
        self.assertEqual(neymar.following.count(), 0)
        self.assertCountEqual(neymar.followers.all(),
                              [User.objects.get(username=user) for user in ["ronaldo", "messi"]])



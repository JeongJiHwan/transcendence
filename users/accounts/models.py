from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    username = models.CharField(max_length=50, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to='accounts/avatars/%Y/%m/%d', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendship_from_set', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_to_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'

    @classmethod
    def add_friend(cls, from_user, to_user):
        # Ensure from_user and to_user are not the same
        if from_user == to_user:
            raise ValueError("Users cannot be friends with themselves.")

        # Ensure the friendship does not already exist
        if cls.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise ValueError("Friendship already exists.")

        # Create the friendship
        friendship = cls(from_user=from_user, to_user=to_user)
        friendship.save()

        return friendship

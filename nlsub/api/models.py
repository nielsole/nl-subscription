import uuid

from django.conf import settings
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class List(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    secret = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return "{} - {}".format(self.name, self.description)


class Subscriber(models.Model):
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    list = models.ForeignKey(List)
    class Meta:
        unique_together = (("list", "email"),)

    def __str__(self):
        return "{} ({})".format(self.email, self.list)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
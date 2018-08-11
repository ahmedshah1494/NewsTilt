"""Model definitions for NewsTilt."""
from __future__ import unicode_literals
import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import login
from django.db.models.signals import post_delete
from django.dispatch import receiver

from NewsTilt.settings import base as base_settings

from .constants import *
from .mixins import *

class Category(models.Model):
    """Categories of news publications and articles."""

    name = models.CharField(max_length=100, null=False, blank=False)
    
    @classmethod
    def get_categories(self):
        cat_names = [(x.name, x.name) for x in Category.objects.all()]
        return cat_names

class MUser(Categorizable, AbstractUser):
    """The custom user class for NT."""

    categories = models.ManyToManyField(Category)
    tilt = models.FloatField(default=0.0)
    view_score = models.FloatField(default=0.0)
    like_score = models.FloatField(default=0.0)
    conformity_score_right = models.FloatField(default=0.0)
    conformity_score_left = models.FloatField(default=0.0)

    def login(self, request):
        """Login the user."""
        return login(request, self.user)

    def subscribe_to(self, category):
        """Subscribe user to a category."""
        return self.add_to(category)

    def unsubscribe_from(self, category):
        """Unsubscribe user from a category."""
        return self.remove_from(category)

class Author(models.Model):
    """Authors enrolled in NT."""

    name = models.CharField(max_length=100, null=False, blank=False)
    tilt = models.FloatField(default=0.0)

class Publication(Categorizable, models.Model):
    """Publications enrolled in NT."""
    
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    categories = models.ManyToManyField(Category)
    image = models.ImageField(upload_to=os.path.join(base_settings.MEDIA_ROOT,
                                                     "publication_icons"))
    authors = models.ManyToManyField(Author)
    tilt = models.FloatField(default=0.0)

class Article(Categorizable, models.Model):
    """Articles in NT."""

    title = models.CharField(max_length=250, null=False, blank=False, unique=True)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Author, null=False)
    source = models.ForeignKey(Publication, null=False)
    url = models.URLField(blank=False, null=False, unique=True)
    image_url = models.URLField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category)
    swipe_score = models.FloatField(default=0.0)
    like_score = models.FloatField(default=0.0)
    view_score = models.FloatField(default=0.0)
    tilt = models.FloatField(default=0.0)

class Action(models.Model):
    """User reaction."""

    user = models.ForeignKey(MUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now_add=True)

class View(Action):

    pass

class Like(Action):
    """docstring for Like."""
    pass

class Swipe(Action):
    """User swipe."""

    direction = models.CharField(max_length=1, choices=[('left','l'), ('right','r')], null=False)
    weight = models.FloatField(default=0.0)
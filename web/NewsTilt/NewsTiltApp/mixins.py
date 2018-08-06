from django.db import models

from .constants import *

class Categorizable(models.Model):
    """Model behaviour for add to or removing from categories."""

    class Meta:
        abstract = True

    def add_to(self, category):
        """Add publication to a category."""
        if category not in self.categories.all():
            self.categories.add(category)
            self.save()
            return SUCCESS
        return CATEGORY_ALREADY_SUBSCRIBED

    def remove_from(self, category):
        """Remvoe publication from a category."""
        if category in self.categories.all():
            self.categories.remove(category)
            self.save()
            return SUCCESS
        return CATEGORY_NOT_SUBSCRIBED
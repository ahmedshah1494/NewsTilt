from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *
from .tilt import *

# @receiver(post_save, sender=Action)
def update_tilts(sender, instance, **kwargs):
    print "updating tilt"
    recalculate_article_tilt(instace.article, instance)
    recalculate_user_tilt(instance.user)
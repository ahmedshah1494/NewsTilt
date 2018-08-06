# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class NewstiltappConfig(AppConfig):
    name = 'NewsTilt.NewsTiltApp'

    def ready(self):
        import signals
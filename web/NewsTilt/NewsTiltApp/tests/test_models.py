from __future__ import unicode_literals

import factory
from django.test import TestCase

from NewsTilt.NewsTiltApp.models import *
from NewsTilt.NewsTiltApp.constants import *

class MUserFactory(factory.Factory):
    
    class Meta:
        model = MUser

    username = factory.Sequence(lambda n: 'user%d' % n)

class CategoryFactory(factory.Factory):
    
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: 'category%d' % n)

class MUserTest(TestCase):        

    def test_create_delete(self):
        init_n_users = len(MUser.objects.all())
        test_users = []
        for i in range(10):
            user = MUserFactory()
            user.save()
            test_users.append(user)
            self.assertEqual(init_n_users+i+1, MUser.objects.count())
        
        for i in range(len(test_users)):
            test_users[i].delete()
            self.assertEqual(init_n_users+len(test_users)-i-1, MUser.objects.count())    
    
    def test_subscribe(self):
        user = MUserFactory()
        user.save()
        cat = CategoryFactory()
        cat.save()

        self.assertEqual(user.subscribe_to(cat), SUCCESS)
        self.assertTrue(user.categories.filter(id=cat.id).exists())

    def test_unsubscribe(self):
        user = MUserFactory()
        user.save()
        cat = CategoryFactory()
        cat.save()

        user.subscribe_to(cat)

        self.assertEqual(user.unsubscribe_from(cat), SUCCESS)
        self.assertFalse(user.categories.filter(id=cat.id).exists())


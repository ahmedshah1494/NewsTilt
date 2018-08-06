import factory
import random
from django.test import TestCase
from NewsTilt.NewsTiltApp.models import *
from NewsTilt.NewsTiltApp.factories import *
from NewsTilt.NewsTiltApp.tilt import *

class TiltTests(TestCase):
    """Test cases for tilt calculation
    """

    # def setUp(self):
    #     self.factory = RequestFactory()

    def test_article_swipe_score_basic(self):
        article = ArticleFactory()
        article.save()

        # Checks if after two left swipes the tilt is -1
        for i in range(2):
            user = MUserFactory()
            user.save()
            swipe = Swipe(user=user, article=article, direction='l')
            swipe.save()
            recalculate_article_tilt(article, swipe)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)

        self.assertEquals(article.tilt, -ARTICLE_SWIPE_WEIGHT)

        # Following that with two right swipes should make it 0, since the weight is 1
        for i in range(2):
            user = MUserFactory()
            user.save()
            swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()
            recalculate_article_tilt(article, swipe)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)

        self.assertEquals(article.tilt, 0)

        # Making two more right swipes should make the tilt positive
        for i in range(2):
            user = MUserFactory()
            user.save()
            swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()
            recalculate_article_tilt(article, swipe)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt > 0.0)

    def test_article_like_score_basic(self):
        article = ArticleFactory()
        article.save()

        # Since the user tilt is 0, like should have no effect
        for i in range(2):
            user = MUserFactory()
            user.save()
            swipe = Like(user=user, article=article)
            swipe.save()
            recalculate_article_tilt(article, swipe)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(article.tilt, 0)

        # An article liked by a rightist should tilt to right
        user = MUserFactory()
        user.tilt = 1.0
        user.save()
        swipe = Like(user=user, article=article)
        swipe.save()
        recalculate_article_tilt(article, swipe)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt > 0.0)

        # A like by a leftist, having the same tilt, should balance it out
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        swipe = Like(user=user, article=article)
        swipe.save()
        recalculate_article_tilt(article, swipe)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(article.tilt, 0.0)

        # Another like by a leftist would tilt it to the left
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        swipe = Like(user=user, article=article)
        swipe.save()
        recalculate_article_tilt(article, swipe)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt < 0.0)

    def test_article_like_score_basic(self):
        article = ArticleFactory()
        article.save()

        # Since the user tilt is 0, view should have no effect
        for i in range(2):
            user = MUserFactory()
            user.save()
            swipe = View(user=user, article=article)
            swipe.save()
            recalculate_article_tilt(article, swipe)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(article.tilt, 0)

        # An article viewed by a rightist should tilt to right
        user = MUserFactory()
        user.tilt = 1.0
        user.save()
        swipe = View(user=user, article=article)
        swipe.save()
        recalculate_article_tilt(article, swipe)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt > 0.0)

        # A view by a leftist, having the same tilt, should balance it out
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        swipe = View(user=user, article=article)
        swipe.save()
        recalculate_article_tilt(article, swipe)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(article.tilt, 0.0)

        # Another view by a leftist would tilt it to the left
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        swipe = View(user=user, article=article)
        swipe.save()
        recalculate_article_tilt(article, swipe)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt < 0.0)
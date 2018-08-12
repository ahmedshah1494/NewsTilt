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

        self.assertTrue(article.tilt < 0)

        # Following that with two right swipes should make it 0, since the weight is 1
        for i in range(2):
            user = MUserFactory()
            user.save()
            swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()
            recalculate_article_tilt(article, swipe)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)

        self.assertEquals(round(article.tilt, 3), 0)

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
            like = Like(user=user, article=article)
            like.save()
            recalculate_article_tilt(article, like)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(article.tilt, 0)

        # An article liked by a rightist should tilt to right
        user = MUserFactory()
        user.tilt = 1.0
        user.save()
        like = Like(user=user, article=article)
        like.save()
        recalculate_article_tilt(article, like)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt > 0.0)

        # A like by a leftist, having the same tilt, should balance it out
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        like = Like(user=user, article=article)
        like.save()
        recalculate_article_tilt(article, like)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(round(article.tilt,3), 0)

        # Another like by a leftist would tilt it to the left
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        like = Like(user=user, article=article)
        like.save()
        recalculate_article_tilt(article, like)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt < 0.0)

    def test_article_view_score_basic(self):
        article = ArticleFactory()
        article.save()

        # Since the user tilt is 0, view should have no effect
        for i in range(2):
            user = MUserFactory()
            user.save()
            view = View(user=user, article=article)
            view.save()
            recalculate_article_tilt(article, view)
            self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(article.tilt, 0)

        # An article viewed by a rightist should tilt to right
        user = MUserFactory()
        user.tilt = 1.0
        user.save()
        view = View(user=user, article=article)
        view.save()
        recalculate_article_tilt(article, view)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt > 0.0)

        # A view by a leftist, having the same tilt, should balance it out
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        view = View(user=user, article=article)
        view.save()
        recalculate_article_tilt(article, view)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertEquals(round(article.tilt,3), 0)

        # Another view by a leftist would tilt it to the left
        user = MUserFactory()
        user.tilt = -1.0
        user.save()
        view = View(user=user, article=article)
        view.save()
        recalculate_article_tilt(article, view)
        self.assertTrue(article.tilt >= -1.0 and article.tilt <= 1.0)
        self.assertTrue(article.tilt < 0.0)

    def test_user_bias_basic(self):
        user = MUserFactory()
        user.save()

        # if user does more left swipes, his right tilt would increase (ceterus paribus)
        for i in range(5):
            article = ArticleFactory()
            article.save()
            if i%2 == 0:
                swipe = Swipe(user=user, article=article, direction='l')
            else:
                swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()
            recalculate_user_tilt(user, swipe)

        self.assertTrue(user.tilt > 0)

        # tilt should become zero when left and right swipes become equal
        article = ArticleFactory()
        article.save()
        swipe = Swipe(user=user, article=article, direction='r')
        swipe.save()
        recalculate_user_tilt(user, swipe)
        self.assertEquals(user.tilt, 0)        

        # left tilt should increase if user makes more right swipes
        article = ArticleFactory()
        article.save()
        swipe = Swipe(user=user, article=article, direction='r')
        swipe.save()
        recalculate_user_tilt(user, swipe)
        self.assertTrue(user.tilt < 0)

    def test_author_tilt_basic(self):
        # Since the user tilt is 0, view should have no effect
        author = AuthorFactory()
        author.save()

        for i in range(2):
            user = MUserFactory()
            user.save()
            article = ArticleFactory(author=author)
            swipe = Swipe(user=user, article=article, direction='l')
            swipe.save()            
            recalculate_article_tilt(article, swipe)
            self.assertTrue(author.tilt >= -1.0 and author.tilt <= 1.0)

        recalculate_author_tilt(author)
        self.assertTrue(author.tilt < 0)

        for i in range(2):
            user = MUserFactory()
            user.save()
            article = ArticleFactory(author=author)
            swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()            
            recalculate_article_tilt(article, swipe)
            self.assertTrue(author.tilt >= -1.0 and author.tilt <= 1.0)

        recalculate_author_tilt(author)
        self.assertEquals(round(author.tilt,3), 0)

        for i in range(2):
            user = MUserFactory()
            user.save()
            article = ArticleFactory(author=author)
            swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()            
            recalculate_article_tilt(article, swipe)
            self.assertTrue(author.tilt >= -1.0 and author.tilt <= 1.0)

        recalculate_author_tilt(author)
        self.assertTrue(author.tilt > 0)

    def test_publication_tilt_basic(self):
        # Since the user tilt is 0, view should have no effect
        source = PublicationFactory()
        source.save()

        for i in range(2):
            user = MUserFactory()
            user.save()
            article = ArticleFactory(source=source)
            swipe = Swipe(user=user, article=article, direction='l')
            swipe.save()            
            recalculate_article_tilt(article, swipe)
            self.assertTrue(source.tilt >= -1.0 and source.tilt <= 1.0)

        recalculate_publication_tilt(source)
        self.assertTrue(source.tilt < 0)

        for i in range(2):
            user = MUserFactory()
            user.save()
            article = ArticleFactory(source=source)
            swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()            
            recalculate_article_tilt(article, swipe)
            self.assertTrue(source.tilt >= -1.0 and source.tilt <= 1.0)

        recalculate_publication_tilt(source)
        self.assertEquals(round(source.tilt,3), 0)

        for i in range(2):
            user = MUserFactory()
            user.save()
            article = ArticleFactory(source=source)
            swipe = Swipe(user=user, article=article, direction='r')
            swipe.save()            
            recalculate_article_tilt(article, swipe)
            self.assertTrue(source.tilt >= -1.0 and source.tilt <= 1.0)

        recalculate_publication_tilt(source)
        self.assertTrue(source.tilt > 0)
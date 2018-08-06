from __future__ import unicode_literals

import factory
from django.test import TestCase

from NewsTilt.NewsTiltApp.models import *
from NewsTilt.NewsTiltApp.scrapers import *
from NewsTilt.NewsTiltApp.serializers import *

class ScraperTest(TestCase):

    def test_structure(self):
        fields = ['title','author','source','url','urlToImage','categories']
        scrapers = get_scraper_list()
        keys = [s.get_top_articles(1)[0].keys() for s in scrapers]
        for i in range(len(keys)):
            for f in fields:
                self.assertTrue(f in keys[i])

    def test_create(self):
        articles = pull_from_all(n_articles=3, enroll=False)
        for article in articles:
            new_article = deserialize_and_enroll(article)

            self.assertEqual(new_article.title, article['title'])
            self.assertEqual(new_article.description, article['description'])
            self.assertEqual(new_article.author.name, article['author'])
            self.assertEqual(new_article.source.name, article['source'])
            self.assertEqual(new_article.url, article['url'])
            if article['urlToImage'] != "":
                self.assertEqual(new_article.image_url, article['urlToImage'])
            for cat in article['categories']:
                self.assertTrue(cat in [x.name for x in new_article.categories.all()])
        # json = {u'description': u'The president and the Republicans claim to have a special understanding of American values and history. But a lot of what they say is very strange.', u'title': u'Op-Ed Columnist: Seven Bizarre Notions Trump and His Team Have About America', u'url': u'https://www.nytimes.com/2017/11/01/opinion/trump-kelly-republicans-history.html', 'category': 'us', u'author': u'ANDREW ROSENTHAL', u'publishedAt': u'2017-11-01T19:51:59Z', u'source': u'The New York Times', u'urlToImage': u'https://static01.nyt.com/images/2017/11/02/opinion/01rosenthalWeb/01rosenthalWeb-facebookJumbo.jpg'}
        # scrapers = get_scraper_list()
        # articles = [s.get_top_articles(1)[0] for s in scrapers]
        # for article in articles:
        #     print article
        #     serializer = ArticleSerializer(data=article)
        #     if not serializer.is_valid():
        #         print serializer.errors
        #         self.assertTrue(False)
        #     new_article = serializer.save()
        #     self.assertTrue(new_article.title == article['title'])
        #     self.assertTrue(new_article.description == article['description'])
        #     self.assertTrue(new_article.author.name == article['author'])
        #     self.assertTrue(new_article.publication.name == article['publication'])
        #     self.assertTrue(new_article.url == article['url'])


"""Code for scrapers to get content from sources which don't have an API."""
import requests
from bs4 import BeautifulSoup
import re
import multiprocessing as mp
from multiprocessing import Process, Pipe
from itertools import izip
from newsapi import NewsApiClient
import time
import os

from NewsTilt.NewsTiltApp.models import *

def exception_wrapper(fun):
    """Wrap fun within a try-catch clause."""
    try:
        return fun()
    except:
        return ""


def run_self(args):
    """Run a class function in a process pool."""
    (C, fun, args) = args
    fun = getattr(C, fun)
    return fun(*args)


class Scraper(object):
    """Parent class for all scraper objects."""

    def __init__(self, url):
        """Initializer."""
        super(Scraper, self).__init__()
        self.url = url

    def get_article_list(self, html):
        """Return the list of articles found on the page."""
        return []

    def parse_article(self, html):
        """Parse the HTML for a an article."""
        return {}

    def get_top_articles(self, n=None):
        """Return the top articles from the source.
        The articles must be a list of dictionaries, which have the following fields:
        - url (string)
        - title (string)
        - description (string)
        - urlToImage (string)
        - author (string)
        - source (string)
        - categories (list)
        """
        r = requests.get(self.url)
        html = r.text

        story_divs = self.get_article_list(html)
        if n is not None:
            story_divs = story_divs[:n]

        # pool = mp.Pool(4)
        # articles = pool.map(run_self, [(self, 'parse_article', (x,)) for x in story_divs])
        articles = [self.parse_article(x) for x in story_divs]
        return articles


class Dawn(Scraper):
    """docstring for Dawn."""

    def __init__(self):
        """Initialize."""
        super(Dawn, self).__init__("https://www.dawn.com/pakistan")

    def get_article_list(self, html):
        """Return the list of articles found on the page."""
        soup = BeautifulSoup(html, 'html.parser')
        story_divs = soup.find_all('article')
        return story_divs

    def parse_article(self, html):
        """Parse the HTML for a an article."""
        article_info = {
            'url': exception_wrapper(lambda: html.h2.a['href']),
        }
        if article_info['url'] == "" or article_info['url'] is None:
            return None
        article_info['title'] = exception_wrapper(lambda: html.h2.a.string)
        article_info['description'] = exception_wrapper(lambda: html.find_all('div',
                                                        attrs={'class': 'story__excerpt'})
                                                        [0].string),
        article_info['urlToImage'] = exception_wrapper(lambda: html.figure.div.a.img['src'])
        article_info['publishedAt'] = exception_wrapper(lambda: html.find_all('span',
                                                        attrs={'class': 'timestamp--time'})
                                                        [0]['title'])

        html = exception_wrapper(lambda: requests.get(article_info['url']).text)
        if html == "":
            return None
        soup = BeautifulSoup(html, 'html.parser')
        author = exception_wrapper(lambda: soup.find_all('span',
                                                         attrs={'class': 'story__byline'})
                                   [0].a.string)
        article_info['author'] = author
        if article_info['author'] == "" or article_info['author'] is None:
            return None

        links = soup.find_all('a', href=re.compile('trends'))
        article_info['categories'] = ['Pakistan']
        tags = exception_wrapper(lambda: [x.string.lower() for x in links])
        article_info['tags'] = [tags]
        article_info['source'] = 'Dawn News'
        return article_info


class ExpressTribune(Scraper):
    """docstring for Scraper."""

    def __init__(self):
        """Initializer."""
        super(ExpressTribune, self).__init__("https://tribune.com.pk/politics/")

    def get_article_list(self, html):
        """Parse the HTML for a an article."""
        soup = BeautifulSoup(html, 'html.parser')
        story_divs = soup.find_all('div', attrs={'class': 'story'})
        return story_divs

    def parse_article(self, html):
        """Return the list of articles found on the page."""
        # print "**",html
        article_info = {
            'url': exception_wrapper(lambda: html.find_all(attrs={'class':'title'})[0].a['href'])
        }
        if article_info['url'] == "" or article_info['url'] is None:
            return None
        article_info['title'] = exception_wrapper(lambda: html.find_all(attrs={'class':'title'})[0].a.string)
        article_info['description'] = exception_wrapper(lambda:
                                                        html.find_all('p', attrs={'class': 'excerpt'})[0].string)
        article_info['urlToImage'] = exception_wrapper(lambda:
                                                       html.find_all('img', attrs={'class': 'story-image'})[0]['src'])
        if article_info['urlToImage'] == '':
            article_info['urlToImage'] = exception_wrapper(lambda:
                                                       html.find_all('a', attrs={'class': 'top-story-image'})[0].img['src'])
        article_info['publishedAt'] = exception_wrapper(lambda:
                                                        html.find_all('span', attrs={'class': 'timestamp'})[0].title)
        article_info['author'] = exception_wrapper(lambda:
                                                   html.find_all('span', attrs={'class': 'author'})[0].string)
        if article_info['author'] == "" or article_info['author'] is None:
            return None
        article_info['source'] = 'Express Tribune'
        article_info['categories'] = ['Pakistan']
        return article_info


class NewsAPI(Scraper):
    """docstring for NewsAPI."""

    def __init__(self):
        """Initializer."""
        self.newsapi = NewsApiClient(api_key=os.environ['NEWSAPI_KEY'])

    def get_top_articles(self, n):
        """Return the top articles from the source."""
        sources = self.newsapi.get_sources(country='us',
                                           category='general')
        sources = sources['sources']
        sources = ['associated-press', 'breitbart-news',
                   'cbs-news', 'cnn','nbc-news',
                   'politico', 'reuters', 'the-huffington-post',
                   'the-washington-post', 'the-washington-times', 'time', 'usa-today',
                   'vice-news']
        # sources = [x['id'] for x in sources]
        sources = str(reduce(lambda x, y: x + ',' + y, sources))

        articles = self.newsapi.get_everything(sources=sources,
                                               language='en',
                                               page_size=n,
                                               sort_by='popularity')
        articles = articles['articles']
        for a in articles:
            a['categories'] = ['US']
            a['source'] = a['source']['name']
        return articles

def get_scraper_list():
    return [Dawn(),
            ExpressTribune(),
            NewsAPI()]    

def deserialize_and_enroll(article):
    """Creates a Article object from the dictionary returned by get_top_articles"""
    if Article.objects.filter(title=article['title'],
                                    url=article['url']).exists():
        return None

    if Author.objects.filter(name=article['author']).exists():
        author = Author.objects.get(name=article['author'])
    else:
        author = Author(name=article['author'])
        author.save()

    if Publication.objects.filter(name=article['source']).exists():
        pub = Publication.objects.get(name=article['source'])
    else:
        pub = Publication(name=article['source'])
        pub.save()

    if not pub.authors.filter(id=author.id).exists():
        pub.authors.add(author)

    new_article = Article(title=article['title'],
                          url=article['url'],
                          author=author,
                          source=pub)
    new_article.save()                                

    for cat in article['categories']:
        if not Category.objects.filter(name=cat).exists():
            category = Category(name=cat)
            category.save()
        else:
            category = Category.objects.get(name=cat)
        pub.add_to(category)
        pub.save()

        new_article.add_to(category)
        new_article.save()
    
    new_article.image_url = article['urlToImage']
    new_article.description = article['description']
    new_article.save()
    return new_article

def pull_from_all(n_articles=10, enroll=False):
    """Pull and enroll articles from all scrapers (and the publications)."""
    scrapers = get_scraper_list()
    articles = [x.get_top_articles(n_articles) for x in scrapers]
    articles = reduce(lambda x, y: x + y, articles)
    articles = filter(lambda x: x is not None, articles)

    if enroll:
        for article in articles:
            deserialize_and_enroll(article)
    
    return articles

        
if __name__ == '__main__':
    t_0 = time.time()
    articles = ExpressTribune().get_top_articles(4)
    print time.time() - t_0
    print articles, len(articles)

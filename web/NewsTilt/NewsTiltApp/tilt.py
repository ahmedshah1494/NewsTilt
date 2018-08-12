import numpy as np
from .models import *
from .constants import *

def recalculate_article_tilt(article, action):
    swipes = Swipe.objects.filter(article=article)
    views = View.objects.filter(article=article)
    likes = Like.objects.filter(article=article)
    user_tilt = action.user.tilt
    if isinstance(action, Swipe):
        score = (-1.0 if action.direction == 'l' else 1.0)*(1-abs(user_tilt))
        n_swipes = swipes.count() + EPS
        article.swipe_score = (article.swipe_score*(n_swipes-1) + score) / n_swipes
        
    if isinstance(action, Like):
        n_likes = likes.count() + EPS
        article.like_score = (article.like_score*(n_likes-1) + user_tilt) / n_likes

    if isinstance(action, View):
        n_views = views.count() + EPS
        article.view_score = (article.view_score*(n_views-1) + user_tilt) / n_views

    article.tilt = ARTICLE_SWIPE_WEIGHT*article.swipe_score + ARTICLE_LIKE_WEIGHT*article.like_score + ARTICLE_VIEW_WEIGHT*article.view_score
    article.save()

def recalculate_user_tilt(user, action):
    right_swipes = Swipe.objects.filter(user=user, direction='r')
    left_swipes = Swipe.objects.filter(user=user, direction='l')
    likes = Like.objects.filter(user=user)
    views = View.objects.filter(user=user)

    n_right_swipes = right_swipes.count() + EPS
    n_left_swipes = left_swipes.count() + EPS
    n_swipes = n_right_swipes + n_left_swipes
    article_tilt = action.article.tilt

    bias_penalty = float(n_left_swipes - n_right_swipes)/n_swipes

    if isinstance(action, Swipe):
        if action.direction == 'l':
            user.conformity_score_left = (user.conformity_score_left*(n_left_swipes-1) + article_tilt) / n_left_swipes
        if action.direction == 'r':
            user.conformity_score_right = (user.conformity_score_right*(n_right_swipes-1) + article_tilt) / n_right_swipes

    if isinstance(action, Like):
        n_likes = likes.count() + EPS
        user.like_score = (user.like_score*(n_likes-1) + article_tilt) / n_likes

    if isinstance(action, View):
        n_views = views.count() + EPS
        user.view_score = (user.view_score*(n_views-1) + article_tilt) / n_views

    conformity_score = 0.5 * (user.conformity_score_right + user.conformity_score_left)
    user.tilt = USER_BIAS_WEIGHT*bias_penalty + USER_CONFORMITY_WEIGHT*conformity_score + USER_LIKE_WEIGHT*user.like_score + USER_VIEW_WEIGHT*user.view_score
    user.save()

def recalculate_author_tilt(author):
    article_tilts = [x.tilt for x in Article.objects.filter(author=author)]
    author.tilt = np.mean(article_tilts)
    author.save()

def recalculate_publication_tilt(pub):
    article_tilts = [x.tilt for x in Article.objects.filter(source=pub)]
    pub.tilt = np.mean(article_tilts)
    pub.save()
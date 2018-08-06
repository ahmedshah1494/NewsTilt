# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import datetime

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from django.contrib.auth import authenticate, login

from .models import *
from .serializers import *

# Create your views here.


def home(request):
    return render(request, 'home.html', {})

@csrf_exempt
@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def signup_new_user(request):
    data = JSONParser().parse(request)
    serializer = MUserSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_user = serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
    if user is None:
        return Response({'error': "Incorrect credentials"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        login(request, user)
        serializer = MUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_user_profile(request):
    serializer = MUserSerializer(request.user)
    return Response({"user":serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_feed(request):
    user = request.user
    print user.categories.all()
    articles = Article.objects.filter(categories__in=user.categories.all())
    serializer = ArticleSerializer(articles, many=True)
    data = serializer.data
    for article in data:
        article['n_likes'] = Like.objects.filter(article=article['id']).count()
        article['n_swipes'] = {}
        article['n_swipes']['l'] = Swipe.objects.filter(article=article['id'], direction='l')
        article['n_swipes']['r'] = Swipe.objects.filter(article=article['id'], direction='r')
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def like_article(request, article_id):
    if not Article.objects.filter(id=article_id).exists():
        return Response({'error': "Article with pk %d does not exist."%article_id}, status=status.HTTP_404_NOT_FOUND)
    article = Article.objects.get(id=article_id)
    if Like.objects.filter(article=article, user=request.user).exists():
        return Response({'error': "Duplicate likes are not permitted"}, status=status.HTTP_400_BAD_REQUEST)
    like = Like(user=request.user, article=article)
    like.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def swipe_article(request, article_id, direction):
    if not Article.objects.filter(id=article_id).exists():
        return Response({'error': "Article with pk %d does not exist."%article_id}, status=status.HTTP_404_NOT_FOUND)
    if direction not in ['l','r']:
        return Response({'error': "Direction must be either 'l' or 'r'"}, status=status.HTTP_400_BAD_REQUEST)
    article = Article.objects.get(id=article_id)
    if Swipe.objects.filter(article=article, user=request.user).exists():
        return Response({'error': "Duplicate swipes are not permitted"}, status=status.HTTP_400_BAD_REQUEST)
    swipe = Swipe(user=request.user, article=article, direction=direction)
    swipe.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def view_article(request, article_id):
    if not Article.objects.filter(id=article_id).exists():
        return Response({'error': "Article with pk %d does not exist."%article_id}, status=status.HTTP_404_NOT_FOUND)
    article = Article.objects.get(id=article_id)
    if View.objects.filter(article=article, user=request.user).exists():
        v = View.objects.get(article=article, user=request.user)
        v.date_modified = datetime.datetime.now()
        v.save()
        return Response(status=status.HTTP_200_OK)    
    v = View(article=article, user=request.user)
    v.save()
    return Response(status=status.HTTP_200_OK)
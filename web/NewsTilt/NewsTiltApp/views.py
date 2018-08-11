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
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .tokens import account_activation_token
from .models import *
from .serializers import *
from .tilt import *

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
        print serializer.errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    user.is_active = False
    user.save()

    current_site = get_current_site(request)
    mail_subject = 'Activate your NewsTilt account.'
    message = render_to_string('verification_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, MUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return Response('Thank you for your email confirmation. Now you can login your account.', status=status.HTTP_200_OK)
    else:
        return HttpResponse('Activation link is invalid!', status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    user = authenticate(request, username=request.data['username'], password=request.data['password'])
    if user is None:
        return Response({'error': "Incorrect credentials"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        login(request, user)
        serializer = MUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def change_password(request):
    if request.user.check_password(request.data['old_password']):
        request.user.set_password(request.data['password'])
        request.user.save()
        return Response('Password changed', status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_user_profile(request):
    serializer = MUserSerializer(request.user)
    return Response({"user":serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_feed(request, n_items):
    user = request.user
    if user.categories.all().count() == 0:
        articles = Article.objects.all()
    else:
        articles = Article.objects.filter(categories__in=user.categories.all())
    serializer = ArticleSerializer(articles, many=True)
    data = serializer.data
    for article in data:
        article['n_likes'] = Like.objects.filter(article=article['id']).count()
        article['n_views'] = View.objects.filter(article=article['id']).count()
        article['n_swipes'] = {}
        article['n_swipes']['l'] = Swipe.objects.filter(article=article['id'], direction='l').count()
        article['n_swipes']['r'] = Swipe.objects.filter(article=article['id'], direction='r').count()
    return Response(data, status=status.HTTP_200_OK)

def update_tilts(instance, **kwargs):
    recalculate_article_tilt(instance.article, instance)
    recalculate_user_tilt(instance.user, instance)

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
    update_tilts(like)
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
    update_tilts(swipe)
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
    view = View(article=article, user=request.user)
    view.save()
    update_tilts(view)
    return Response(status=status.HTTP_200_OK)
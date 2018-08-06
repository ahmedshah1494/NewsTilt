from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id','name']
        model = Category

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id','name','tilt']
        model = Author

class PublicationSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    authors = AuthorSerializer(many=True)
    class Meta:
        fields = ['id','name', 'categories', 'image', 'authors', 'tilt']
        model = Publication

class MUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(label='First Name', max_length=100, required=True)
    last_name = serializers.CharField(label='Last Name', max_length=100, required=True)
    username = serializers.CharField(label='Username', max_length=20, required=True)
    password = serializers.CharField(label='Password', max_length=100, required=True)
    categories = CategorySerializer(many=True)

    class Meta:
        fields = ['first_name', 'last_name', 'username', 'categories', 'tilt', 'password']
        model = MUser
    def create(self, data):
        new_user = MUser(username=data['username'],
                                first_name=data['first_name'],
                                last_name=data['last_name'])
        new_user.set_password(data['password'])
        new_user.save()
        for cat in data['categories']:
            cat = dict(cat)
            cat = Category.objects.filter(name=cat['name'])
            new_user.subscribe_to(cat[0])
        new_user.save()
        return new_user

class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    source = PublicationSerializer()
    categories = CategorySerializer(many=True)
    class Meta:
        fields = ['id','title','description','url','image_url','date_added', 'tilt','categories', 'author', 'source']
        model = Article
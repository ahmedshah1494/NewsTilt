class ArticleSerializer(serializers.Serializer):

    title = serializers.CharField(max_length=250)
    author = serializers.CharField()
    source = serializers.CharField()
    url = serializers.CharField()
    urlToImage = serializers.CharField(allow_blank=True)
    category = CategorySerializer(many=True)

    def validate_author(self, value):
        if value == '':
            raise serializers.ValidationError("Author can not be null.")
        if not Author.objects.filter(name=value).exists():
            author = Author(name=value)
            author.save()
        else:
            author = Author.objects.get(name=value)
        return author

    def validate_category(self, value):
        if value == '':
            raise serializers.ValidationError("Category can not be null.")
        if not Category.objects.filter(name=value).exists():
            category = Category(name=value)
            category.save()
        else:
            category = Category.objects.get(name=value)
        return category

    def validate_source(self, value):
        if value == '':
            raise serializers.ValidationError("Source can not be null.")
        if not Publication.objects.filter(name=value).exists():
            pub = Publication(name=value)
            pub.save()
        else:
            pub = Publication.objects.get(name=value)
        pub.save()
        return pub

    def validate(self, data):
        if Article.objects.filter(title=data['title'],
                                    url=data['url']).exists():
            raise serializers.ValidationError("Article already exists.")
        return data

    def create(self, data):
        pub = data['source']
        new_article = Article(title=data['title'],
                              url=data['url'],
                              source=data['source'],
                              author=data['author'])

        
        if data['urlToImage'] != "":
            new_article.image_url = data['urlToImage']

        new_article.save()
        return new_article
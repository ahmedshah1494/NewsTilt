import factory
from NewsTilt.NewsTiltApp.models import *

class CategoryFactory(factory.Factory):
    
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: "category%d" % n)

class MUserFactory(factory.Factory):
    
    class Meta:
        model = MUser

    username = factory.Sequence(lambda n: "user%d" % n)

class AuthorFactory(factory.DjangoModelFactory):
    
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: "Author%d" % n)

class PublicationFactory(factory.DjangoModelFactory):

    class Meta:
        model = Publication

    name = factory.Sequence(lambda n: "Pub%d" % n)

class ArticleFactory(factory.DjangoModelFactory):

    class Meta:
        model = Article

    title = factory.Sequence(lambda n: "Article%d" % n)
    url = factory.Sequence(lambda n: "url%d" % n)
    author = factory.SubFactory(AuthorFactory)
    source = factory.SubFactory(PublicationFactory)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for cat in extracted:
                self.categories.add(cat)
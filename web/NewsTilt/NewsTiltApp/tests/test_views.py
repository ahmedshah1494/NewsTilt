import random
from django.test import TestCase, RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware
from NewsTilt.NewsTiltApp.models import *
from NewsTilt.NewsTiltApp.views import *
from NewsTilt.NewsTiltApp.factories import *

def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class()
    middleware.process_request(request)
    return request

def add_middleware_to_response(response, middleware_class):
    middleware = middleware_class()
    middleware.process_response(response)
    return response

class ViewTests(TestCase):
    """Test cases for each function in views.py
       test_{function_name}
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
    def test_get_categories(self):
        for i in range(5):
            CategoryFactory().save()

        request = self.factory.get("/get_categories")
        response = get_categories(request)
        
        categories = Category.objects.all()
        for c in categories:
            self.assertContains(response, c.name)

    def test_signup_new_user(self):
        for i in range(5):
            CategoryFactory().save()

        # Check if user is created
        cats = [x.name for x in Category.objects.all()][:2]
        request = self.factory.post("/signup", '{"first_name": "John","last_name": "Doe","username": "johndoe","password": "123","categories": [{"name": "%s"},{"name": "%s"}]}' % tuple(cats), content_type="application/json")
        response = signup_new_user(request)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(MUser.objects.filter(username="johndoe").exists())

        # Check if the data for the new user is correct
        user = MUser.objects.get(username="johndoe")
        self.assertEquals(user.first_name, "John")
        self.assertEquals(user.last_name, "Doe")
        self.assertTrue(cats[0] in [x.name for x in user.categories.all()])
        self.assertTrue(cats[1] in [x.name for x in user.categories.all()])
        self.assertFalse(user.is_active)

    def test_login_user(self):
        user = MUser(first_name='John',
                     last_name='Doe',
                     username='johndoe')
        user.set_password('123')
        user.save()

        # Check valid login
        request = self.factory.post('/login', {"username": "johndoe", "password":"123"})
        add_middleware_to_request(request, SessionMiddleware)
        response = login_user(request)
        self.assertEquals(response.status_code, 200)        

        # Check invalid logins
        request = self.factory.post('/login', {"username": "xyz", "password":"123"})
        add_middleware_to_request(request, SessionMiddleware)
        response = login_user(request)
        self.assertEquals(response.status_code, 400)

        request = self.factory.post('/login', {"username": "johndoe", "password":"12"})
        add_middleware_to_request(request, SessionMiddleware)
        response = login_user(request)
        self.assertEquals(response.status_code, 400)

    def test_change_password(self):
        user = MUser(first_name='John',
                     last_name='Doe',
                     username='johndoe')
        user.set_password('123')
        user.save()

        self.client.login(username='johndoe', password='123')
        response = self.client.post('/change_password', {'old_password': '123', 'password':'456'})        
        self.assertEquals(response.status_code, 200)
        self.assertTrue(MUser.objects.get(username='johndoe').check_password('456'))

        self.client.login(username='johndoe', password='456')
        response = self.client.post('/change_password', {'old_password': '123', 'password':'789'})
        self.assertEquals(response.status_code, 400)
        self.assertTrue(MUser.objects.get(username='johndoe').check_password('456'))

    def test_get_user_profile(self):
        user = MUser(first_name='John',
                     last_name='Doe',
                     username='johndoe')
        user.set_password('123')
        user.save()

        # Check if logged in user gets the profile and an unauthenticated user doesnt
        request = self.factory.get('/profile')
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = get_user_profile(request)
        self.assertEquals(response.status_code, 200)

        request = self.factory.get('/profile')
        add_middleware_to_request(request, SessionMiddleware)
        response = get_user_profile(request)
        self.assertEquals(response.status_code, 403)

    def test_get_feed(self):
        user = MUser(first_name='John',
                     last_name='Doe',
                     username='johndoe')
        user.set_password('123')
        user.save()

        for i in range(10):
            CategoryFactory().save()
        cats = Category.objects.all()
        
        for i in range(10):
            ArticleFactory.create(categories=[random.choice(cats), random.choice(cats)]).save()

        request = self.factory.get('/feed/3')
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = get_feed(request,3)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 3)

        my_cats = Category.objects.all()[:2]
        for cat in my_cats:
            user.subscribe_to(cat)
        request = self.factory.get('/feed/3')
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = get_feed(request,3)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), Article.objects.filter(categories__in=my_cats).count())
        for a in response.data:
            article_cats = [x['name'] for x in a['categories']]
            self.assertTrue(reduce(lambda x,y: x or y, [c.name in article_cats for c in my_cats]))

    def test_like_article(self):
        user = MUser(first_name='John',
                     last_name='Doe',
                     username='johndoe')
        user.set_password('123')
        user.save()

        article = ArticleFactory()
        article.save()

        request = self.factory.get('/like/%d'%(article.id+1))
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = like_article(request, article.id+1)
        self.assertEquals(response.status_code, 404)

        request = self.factory.get('/like/%d'%article.id)
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = like_article(request, article.id)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(Like.objects.filter(article=article, user=request.user).exists())

        request = self.factory.get('/like/%d'%article.id)
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = like_article(request, article.id)
        self.assertEquals(response.status_code, 400)

        request = self.factory.get('/like/%d'%article.id)
        request.user = MUserFactory()
        request.user.save()
        add_middleware_to_request(request, SessionMiddleware)
        response = like_article(request, article.id)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(Like.objects.filter(article=article, user=request.user).exists())

    def test_swipe_article(self):
        user = MUser(first_name='John',
                     last_name='Doe',
                     username='johndoe')
        user.set_password('123')
        user.save()

        article = ArticleFactory()
        article.save()

        request = self.factory.get('/like/%d/l'%(article.id+1))
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = swipe_article(request, article.id+1, 'l')
        self.assertEquals(response.status_code, 404)

        request = self.factory.get('/like/%d/l'%article.id)
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = swipe_article(request, article.id, 'l')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(Swipe.objects.filter(article=article, user=request.user, direction='l').exists())

        request = self.factory.get('/like/%d/r'%article.id)
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = swipe_article(request, article.id, 'r')
        self.assertEquals(response.status_code, 400)
        self.assertFalse(Swipe.objects.filter(article=article, user=request.user, direction='r').exists())

        request = self.factory.get('/like/%d/l'%article.id)
        request.user = MUserFactory()
        request.user.save()
        add_middleware_to_request(request, SessionMiddleware)
        response = swipe_article(request, article.id, 'l')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(Swipe.objects.filter(article=article, user=request.user, direction='l').exists())

    def test_view_article(self):
        user = MUser(first_name='John',
                     last_name='Doe',
                     username='johndoe')
        user.set_password('123')
        user.save()

        article = ArticleFactory()
        article.save()

        request = self.factory.get('/view/%d'%(article.id+1))
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = view_article(request, article.id+1)
        self.assertEquals(response.status_code, 404)

        request = self.factory.get('/view/%d'%article.id)
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = view_article(request, article.id)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(View.objects.filter(article=article, user=request.user).exists())

        prev_dt = View.objects.get(article=article, user=request.user).date_modified
        request = self.factory.get('/view/%d'%article.id)
        request.user = user
        add_middleware_to_request(request, SessionMiddleware)
        response = view_article(request, article.id)
        self.assertEquals(response.status_code, 200)
        curr_dt = View.objects.get(article=article, user=request.user).date_modified
        self.assertTrue(curr_dt > prev_dt)


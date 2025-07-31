import factory
from a_reviews.models import Review, Course
from django.contrib.auth.models import User
import random


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User  
        django_get_or_create = ('username',)

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence(lambda n: 'user%d' % n)



class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    code = factory.Sequence(lambda n: f"COURSE{n:03d}")
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')
    sessions = factory.LazyFunction(lambda: ['2025-Autumn', '2026-Spring'])  # example JSON list
    page_reference = factory.Faker('url')
    faculty = factory.Faker('company')


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    course = factory.SubFactory(CourseFactory)
    author = factory.SubFactory(UserFactory)
    
    overall_rating = factory.LazyFunction(lambda: random.randint(1, 5))
    enjoyment = factory.LazyFunction(lambda: random.randint(1, 5))
    usefullness = factory.LazyFunction(lambda: random.randint(1, 5))
    manageability = factory.LazyFunction(lambda: random.randint(1, 5))
    course_completion = factory.LazyFunction(lambda: f"{random.randint(2020, 2025)}-{random.choice(['Autumn', 'Spring', 'Summer'])}")
    
    title = factory.Faker('sentence', nb_words=4)
    text_review = factory.Faker('paragraph')
    grade = factory.LazyFunction(lambda: random.choice([None, 70, 85, 90]))
    is_anonymous = factory.Faker('boolean')

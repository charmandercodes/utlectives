import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from a_reviews.models import Course, Review


class Command(BaseCommand):
    help = 'Create 20 test reviews for a specific course'

    def add_arguments(self, parser):
        parser.add_argument(
            'course_name',
            type=str,
            help='Name of the course to create reviews for (e.g., "Web Systems")'
        )

    def handle(self, *args, **options):
        course_name = options['course_name']
        
        # Find the course
        try:
            course = Course.objects.get(name__icontains=course_name)
            self.stdout.write(f"Found course: {course.code} - {course.name}")
        except Course.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Course with name containing '{course_name}' not found!")
            )
            return
        except Course.MultipleObjectsReturned:
            courses = Course.objects.filter(name__icontains=course_name)
            self.stdout.write(
                self.style.ERROR(f"Multiple courses found containing '{course_name}':")
            )
            for c in courses:
                self.stdout.write(f"  - {c.code}: {c.name}")
            self.stdout.write("Please be more specific.")
            return

        # Create 20 test users if they don't exist
        test_users = []
        with transaction.atomic():
            for i in range(20):
                username = f"testuser{i+1}"
                email = f"testuser{i+1}@example.com"
                
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': f"Test",
                        'last_name': f"User{i+1}",
                    }
                )
                test_users.append(user)
                
                if created:
                    self.stdout.write(f"Created user: {username}")

        # Review content templates
        review_titles = [
            "Great course!",
            "Really enjoyed this",
            "Challenging but worth it",
            "Excellent professor",
            "Good learning experience",
            "Well structured course",
            "Highly recommend",
            "Solid course content",
            "Engaging lectures",
            "Practical and useful",
            "Could be better",
            "Needs improvement",
            "Average course",
            "Not my favorite",
            "Okay experience"
        ]

        review_texts = [
            "This course exceeded my expectations. The content was well-organized and the assignments were meaningful.",
            "Really enjoyed the practical approach to learning. The professor was knowledgeable and engaging.",
            "Challenging course but I learned a lot. Would recommend to anyone interested in the subject.",
            "Great mix of theory and practice. The workload was manageable and the material was relevant.",
            "Excellent course structure. Each week built upon the previous, making it easy to follow along.",
            "The professor was amazing and really cared about student learning. Highly recommend!",
            "Good course overall. Some parts were a bit dry but the important concepts were covered well.",
            "Learned so much in this course! The assignments really helped reinforce the concepts.",
            "Well-designed course with clear expectations. The feedback on assignments was very helpful.",
            "Interesting subject matter and good teaching approach. Would take another course from this professor.",
            "The course was okay but could use some updates to the curriculum and teaching methods.",
            "Content was relevant but the pace was a bit too fast for my liking.",
            "Average course experience. Some good parts but also room for improvement.",
            "The workload was quite heavy but manageable if you stay on top of it.",
            "Good introduction to the subject. Would be helpful to have more practical examples."
        ]

        # Course completion options
        seasons = ['Autumn', 'Spring', 'Summer']
        years = [2023, 2024, 2025]

        # Create exactly 20 reviews
        created_reviews = []
        with transaction.atomic():
            for i, user in enumerate(test_users):
                # Skip if review already exists
                if Review.objects.filter(course=course, author=user).exists():
                    self.stdout.write(f"Review already exists for {user.username}, skipping...")
                    continue
                
                # Generate random ratings
                overall_rating = random.randint(1, 5)
                enjoyment = random.randint(1, 5)
                usefulness = random.randint(1, 5)
                manageability = random.randint(1, 5)
                
                # Generate course completion
                year = random.choice(years)
                season = random.choice(seasons)
                course_completion = f"{year}-{season}"
                
                # Random optional fields
                title = random.choice(review_titles) if random.random() > 0.2 else None
                text_review = random.choice(review_texts) if random.random() > 0.3 else None
                grade = random.randint(50, 100) if random.random() > 0.4 else None
                is_anonymous = random.random() > 0.7
                
                # Create review
                review = Review.objects.create(
                    course=course,
                    author=user,
                    overall_rating=overall_rating,
                    enjoyment=enjoyment,
                    usefullness=usefulness,
                    manageability=manageability,
                    course_completion=course_completion,
                    title=title,
                    text_review=text_review,
                    grade=grade,
                    is_anonymous=is_anonymous
                )
                
                created_reviews.append(review)
                self.stdout.write(f"Created review #{len(created_reviews)} by {user.username}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(created_reviews)} reviews for {course.name}!"
            )
        )
        
        # Show final summary
        total_reviews = Review.objects.filter(course=course).count()
        self.stdout.write(f"\nTotal reviews for {course.name}: {total_reviews}")
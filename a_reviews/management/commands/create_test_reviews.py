import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from a_reviews.models import Course, Review


class Command(BaseCommand):
    help = 'Create 1-10 random test reviews for each course in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-users',
            type=int,
            default=50,
            help='Maximum number of test users to create (default: 50)'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all test reviews and test users instead of creating them'
        )

    def handle(self, *args, **options):
        max_users = options['max_users']
        delete_mode = options['delete']
        
        if delete_mode:
            self.delete_test_data()
            return
        
        # Get all courses
        courses = Course.objects.all()
        if not courses.exists():
            self.stdout.write(
                self.style.ERROR("No courses found! Please create some courses first.")
            )
            return
        
        self.stdout.write(f"Found {courses.count()} courses")

        # Create test users if they don't exist
        test_users = []
        with transaction.atomic():
            for i in range(max_users):
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
            "Okay experience",
            "Loved every minute",
            "Tough but fair",
            "Would take again",
            "Life-changing course",
            "Boring lectures"
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
            "Good introduction to the subject. Would be helpful to have more practical examples.",
            "Outstanding course with real-world applications. Highly valuable for career development.",
            "Difficult material but the professor explained concepts clearly. Great support from TAs.",
            "The group projects were excellent for learning collaboration skills.",
            "Course content felt outdated and could benefit from modernization.",
            "Minimal effort required but also minimal learning. Expected more depth."
        ]

        # Course completion options
        seasons = ['Autumn', 'Spring', 'Summer']
        years = [2022, 2023, 2024, 2025]

        total_reviews_created = 0
        
        # Process each course
        for course in courses:
            self.stdout.write(f"\nProcessing course: {course.code} - {course.name}")
            
            # Determine random number of reviews for this course (1-10)
            num_reviews = random.randint(1, 10)
            self.stdout.write(f"Will create {num_reviews} reviews for this course")
            
            # Get random users for this course (ensure we don't exceed available users)
            available_users = [user for user in test_users 
                             if not Review.objects.filter(course=course, author=user).exists()]
            
            if len(available_users) < num_reviews:
                self.stdout.write(
                    self.style.WARNING(
                        f"Only {len(available_users)} users available (no existing reviews), "
                        f"creating {len(available_users)} reviews instead of {num_reviews}"
                    )
                )
                num_reviews = len(available_users)
            
            # Select random users for this course
            selected_users = random.sample(available_users, num_reviews)
            
            # Create reviews for this course
            course_reviews_created = 0
            with transaction.atomic():
                for user in selected_users:
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
                        usefullness=usefulness,  # Note: keeping original spelling from your model
                        manageability=manageability,
                        course_completion=course_completion,
                        title=title,
                        text_review=text_review,
                        grade=grade,
                        is_anonymous=is_anonymous
                    )
                    
                    course_reviews_created += 1
                    total_reviews_created += 1
                    self.stdout.write(f"  Created review by {user.username}")

            self.stdout.write(
                self.style.SUCCESS(f"Created {course_reviews_created} reviews for {course.name}")
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Created {total_reviews_created} total reviews across {courses.count()} courses."
            )
        )
        
        # Show final summary
        self.stdout.write("\nFinal summary:")
        for course in courses:
            review_count = Review.objects.filter(course=course).count()
            self.stdout.write(f"  {course.code}: {review_count} reviews")

    def delete_test_data(self):
        """Delete all test reviews and test users"""
        self.stdout.write("Starting deletion of test data...")
        
        # Delete reviews by test users
        test_usernames = [f"testuser{i+1}" for i in range(200)]  # Cover up to 200 test users
        test_users = User.objects.filter(username__in=test_usernames)
        
        if test_users.exists():
            # Get affected courses before deletion
            affected_courses = set()
            reviews_to_delete = Review.objects.filter(author__in=test_users)
            for review in reviews_to_delete:
                affected_courses.add(review.course)
            
            # Delete reviews first
            reviews_deleted = reviews_to_delete.delete()
            self.stdout.write(f"Deleted {reviews_deleted[0]} test reviews")
            
            # Update ratings for affected courses
            self.stdout.write("Updating course ratings...")
            for course in affected_courses:
                course.update_ratings()
            self.stdout.write(f"Updated ratings for {len(affected_courses)} courses")
            
            # Delete test users
            users_deleted = test_users.delete()
            self.stdout.write(f"Deleted {users_deleted[0]} test users")
            
            self.stdout.write(
                self.style.SUCCESS("Successfully deleted all test data!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("No test users found to delete.")
            )
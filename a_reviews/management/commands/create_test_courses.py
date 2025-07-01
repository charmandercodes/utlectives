import random
from django.core.management.base import BaseCommand
from django.db import transaction
from a_reviews.models import Course  # Adjust import path to your app


class Command(BaseCommand):
    help = 'Create test courses with random data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of courses to create (default: 30)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Define the faculties and sessions
        faculties = [
            'Analytics',
            'Business', 
            'Engineering',
            'Law',
            'Health',
            'Science',
            'IT'
        ]
        
        sessions = [
            'Autumn',
            'Spring', 
            'Summer',
            'July',
            'Unavailable'
        ]
        
        # Course name templates for variety
        course_name_templates = [
            "Introduction to {}",
            "Advanced {}",
            "Fundamentals of {}",
            "{} Systems",
            "{} Analysis",
            "{} Management",
            "{} Theory",
            "{} Practice",
            "Applied {}",
            "{} Research",
            "{} Design",
            "{} Development",
            "Modern {}",
            "{} Applications",
            "{} Principles"
        ]
        
        # Subject areas for course names
        subjects = [
            "Data Science", "Machine Learning", "Algorithms", "Database Systems",
            "Web Development", "Software Engineering", "Computer Networks", 
            "Cybersecurity", "Artificial Intelligence", "Mobile Development",
            "Cloud Computing", "DevOps", "User Experience", "Project Management",
            "Business Analytics", "Financial Modeling", "Marketing Strategy",
            "Operations Research", "Supply Chain", "Digital Transformation",
            "Constitutional Law", "Corporate Law", "Criminal Justice", "Legal Ethics",
            "Public Health", "Biomedical Sciences", "Nursing Practice", "Medical Ethics",
            "Physics", "Chemistry", "Biology", "Mathematics", "Statistics", 
            "Environmental Science", "Geology", "Astronomy", "Biotechnology"
        ]
        
        # Description templates
        descriptions = [
            "This course provides a comprehensive introduction to key concepts and methodologies.",
            "Students will explore advanced techniques and real-world applications in this field.",
            "A practical course focusing on hands-on experience and industry-relevant skills.",
            "This subject covers theoretical foundations and contemporary research developments.",
            "An intensive program designed to develop critical thinking and analytical skills.",
            "Students will engage with current challenges and emerging trends in the discipline.",
            "This course combines theoretical knowledge with practical implementation strategies.",
            "A research-oriented subject exploring cutting-edge developments and innovations.",
            "Students will develop professional competencies through project-based learning.",
            "This comprehensive course covers both fundamental principles and advanced applications."
        ]

        created_courses = []
        
        with transaction.atomic():
            for i in range(count):
                # Generate unique course code
                while True:
                    code = f"{random.choice(['CS', 'IT', 'BUS', 'LAW', 'SCI', 'ENG', 'HLT'])}{random.randint(10000, 99999)}"
                    if not Course.objects.filter(code=code).exists():
                        break
                
                # Generate course name
                template = random.choice(course_name_templates)
                subject = random.choice(subjects)
                if '{}' in template:
                    name = template.format(subject)
                else:
                    name = f"{template} {subject}"
                
                # Ensure name doesn't exceed 50 characters
                if len(name) > 50:
                    name = name[:47] + "..."
                
                # Generate random ratings (0-5 scale)
                enjoyment = round(random.uniform(1.0, 5.0), 1)
                usefulness = round(random.uniform(1.0, 5.0), 1)
                manageability = round(random.uniform(1.0, 5.0), 1)
                overall_rating = round(random.uniform(1.0, 5.0), 1)
                
                # Randomly select 1-3 sessions
                num_sessions = random.randint(1, 3)
                course_sessions = random.sample(sessions, num_sessions)
                
                # Select faculty
                faculty = random.choice(faculties)
                
                # Select description
                description = random.choice(descriptions)
                
                # Create course
                course = Course.objects.create(
                    code=code,
                    name=name,
                    description=description,
                    enjoyment=enjoyment,
                    usefullness=usefulness,  # Note: keeping your spelling
                    manageability=manageability,
                    overall_rating=overall_rating,
                    sessions=course_sessions,
                    faculty=faculty,
                    page_reference=f"https://handbook.uts.edu.au/subjects/{code.lower()}.html"
                )
                
                created_courses.append(course)
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    self.stdout.write(f"Created {i + 1}/{count} courses...")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(created_courses)} test courses!"
            )
        )
        
        # Display some sample courses
        self.stdout.write("\nSample courses created:")
        for course in created_courses[:5]:
            self.stdout.write(
                f"  {course.code}: {course.name} ({course.faculty}) - "
                f"Sessions: {', '.join(course.sessions)} - "
                f"Rating: {course.overall_rating}/5"
            )
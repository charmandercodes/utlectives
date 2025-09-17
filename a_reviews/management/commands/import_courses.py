import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from a_reviews.models import Course

class Command(BaseCommand):
    help = "Import courses from a JSON file/folder or delete courses"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the JSON file containing courses'
        )
        parser.add_argument(
            '--folder',
            type=str,
            help='Path to folder containing JSON files (will process all .json files)'
        )
        parser.add_argument(
            '--delete-all',
            action='store_true',
            help='Delete all courses from the database'
        )
        parser.add_argument(
            '--delete-by',
            action='store_true',
            help='Delete courses by faculty and/or level (use with --faculty and/or --level)'
        )
        parser.add_argument(
            '--faculty',
            type=str,
            help='Faculty to filter by (for deletion or display)'
        )
        parser.add_argument(
            '--level',
            type=str,
            choices=['UG', 'PG'],
            help='Level to filter by: UG (Undergraduate) or PG (Postgraduate)'
        )
        parser.add_argument(
            '--postgrad',
            action='store_true',
            help='Import courses as postgraduate level (default is undergraduate)'
        )

    def load_courses_from_file(self, file_path):
        """Load courses from a single JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'subjects' in data:
                    return data['subjects']
                elif 'courses' in data:
                    return data['courses']
                elif 'data' in data and isinstance(data['data'], list):
                    return data['data']
                else:
                    return [data]  # Single course as dict
            
            return []
        except Exception as e:
            self.stderr.write(f"Error reading {file_path}: {e}")
            return []

    def import_courses_from_data(self, courses_data, level, level_display, source_name=""):
        """Import courses from data list."""
        created_count = 0
        updated_count = 0
        
        for course_item in courses_data:
            code = course_item.get("code")
            title = course_item.get("title")
            
            if not code or not title:
                self.stderr.write(f"Skipping invalid course in {source_name}: missing code or title")
                continue
                
            description = course_item.get("description", "")
            teaching_period = course_item.get("teachingPeriod", "")
            base_url = "https://coursehandbook.uts.edu.au"
            url_path = course_item.get("URL_MAP_FOR_CONTENT", "")
            full_url = base_url + url_path
            faculty = course_item.get("educationalAreaDisplay", "")

            # Create or update the Course
            course, created = Course.objects.update_or_create(
                code=code,
                defaults={
                    'name': title,
                    'description': description,
                    'page_reference': full_url,
                    'faculty': faculty,
                    'sessions': teaching_period if teaching_period else [],
                    'level': level,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created {level_display} course {code} - {title}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated {level_display} course {code} - {title}"))
        
        return created_count, updated_count

    def handle(self, *args, **options):
        # Handle deletion by faculty/level
        if options['delete_by']:
            filter_kwargs = {}
            
            if options['faculty']:
                filter_kwargs['faculty'] = options['faculty']
            
            if options['level']:
                filter_kwargs['level'] = options['level']
            
            if not filter_kwargs:
                self.stderr.write("Please provide --faculty and/or --level when using --delete-by")
                return
            
            courses_to_delete = Course.objects.filter(**filter_kwargs)
            count = courses_to_delete.count()
            
            if count == 0:
                self.stdout.write(self.style.WARNING("No courses found matching the criteria."))
                return
            
            # Show what will be deleted
            filter_description = []
            if options['faculty']:
                filter_description.append(f"faculty='{options['faculty']}'")
            if options['level']:
                level_display = 'Undergraduate' if options['level'] == 'UG' else 'Postgraduate'
                filter_description.append(f"level={level_display}")
            
            self.stdout.write(f"Found {count} courses matching {' and '.join(filter_description)}")
            
            # Delete the courses
            courses_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} courses."))
            
            # Exit if only deleting
            if not options['file'] and not options['folder']:
                return

        # Handle deletion of all courses
        if options['delete_all']:
            count, _ = Course.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} courses from the database."))
            # Exit if only deleting
            if not options['file'] and not options['folder']:
                return

        # Check if we have a file or folder to import
        if not options['file'] and not options['folder']:
            self.stderr.write("Please provide either --file or --folder for importing courses")
            return
        
        if options['file'] and options['folder']:
            self.stderr.write("Please provide either --file OR --folder, not both")
            return

        # Determine the level based on the postgrad flag
        level = 'PG' if options['postgrad'] else 'UG'
        level_display = 'Postgraduate' if options['postgrad'] else 'Undergraduate'
        
        total_created = 0
        total_updated = 0
        
        if options['file']:
            # Import single file
            file_path = options['file']
            self.stdout.write(f"Importing courses from {file_path} as {level_display} level...")
            
            courses_data = self.load_courses_from_file(file_path)
            if courses_data:
                created, updated = self.import_courses_from_data(
                    courses_data, level, level_display, file_path
                )
                total_created += created
                total_updated += updated
        
        elif options['folder']:
            # Import all JSON files in folder
            folder_path = Path(options['folder'])
            
            if not folder_path.exists():
                self.stderr.write(f"Folder does not exist: {folder_path}")
                return
            
            if not folder_path.is_dir():
                self.stderr.write(f"Path is not a directory: {folder_path}")
                return
            
            # Find all JSON files
            json_files = list(folder_path.glob('*.json'))
            
            if not json_files:
                self.stderr.write(f"No JSON files found in folder: {folder_path}")
                return
            
            self.stdout.write(f"Found {len(json_files)} JSON files in {folder_path}")
            self.stdout.write(f"Importing courses as {level_display} level...")
            
            for json_file in json_files:
                self.stdout.write(f"\nProcessing: {json_file.name}")
                
                courses_data = self.load_courses_from_file(json_file)
                if courses_data:
                    created, updated = self.import_courses_from_data(
                        courses_data, level, level_display, json_file.name
                    )
                    total_created += created
                    total_updated += updated
                    self.stdout.write(f"  -> {created} created, {updated} updated from {json_file.name}")
                else:
                    self.stdout.write(self.style.WARNING(f"  -> No valid courses found in {json_file.name}"))

        # Final summary
        self.stdout.write(self.style.SUCCESS(f"\nImport complete!"))
        self.stdout.write(f"Total courses created: {total_created}")
        self.stdout.write(f"Total courses updated: {total_updated}")
        self.stdout.write(f"Total courses processed: {total_created + total_updated}")
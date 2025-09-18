from django.core.management.base import BaseCommand
from django.db.models import Q
from a_reviews.models import Course  # Replace 'your_app' with your actual app name
import json

class Command(BaseCommand):
    help = 'Extract unique sessions from Course.sessions field and display them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['list', 'json', 'choices', 'sql'],
            default='list',
            help='Output format (default: list)'
        )
        parser.add_argument(
            '--save-to-file',
            type=str,
            help='Save output to specified file'
        )
        parser.add_argument(
            '--show-stats',
            action='store_true',
            help='Show statistics about session usage'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Analyzing Course sessions...\n')
        )

        # Get all courses that have sessions
        courses_with_sessions = Course.objects.exclude(
            Q(sessions__isnull=True) | Q(sessions=[])
        )

        if not courses_with_sessions.exists():
            self.stdout.write(
                self.style.WARNING('No courses found with sessions.')
            )
            return

        # Extract unique sessions
        unique_sessions = set()
        session_stats = {}
        courses_analyzed = 0

        for course in courses_with_sessions:
            courses_analyzed += 1
            if course.sessions:
                for session in course.sessions:
                    if session:  # Skip empty strings/None
                        session = session.strip()  # Clean whitespace
                        if session:  # Double check after stripping
                            unique_sessions.add(session)
                            session_stats[session] = session_stats.get(session, 0) + 1

        # Sort sessions (try to sort logically)
        sorted_sessions = self.sort_sessions_logically(list(unique_sessions))

        # Display results based on format
        output_content = self.format_output(
            sorted_sessions, 
            session_stats, 
            options['format'], 
            courses_analyzed,
            options['show_stats']
        )

        # Output to console
        self.stdout.write(output_content)

        # Save to file if requested
        if options['save_to_file']:
            try:
                with open(options['save_to_file'], 'w') as f:
                    f.write(output_content)
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Output saved to {options["save_to_file"]}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error saving to file: {e}')
                )

    def sort_sessions_logically(self, sessions):
        """Sort sessions in a logical order (seasons, then alphabetically)"""
        season_order = {
            'SPRING': 1,
            'SUMMER': 2, 
            'AUTUMN': 3,
            'FALL': 3,  # Treat FALL same as AUTUMN
            'WINTER': 4
        }
        
        def sort_key(session):
            session_upper = session.upper()
            # Check if it's a known season
            for season, order in season_order.items():
                if season in session_upper:
                    return (order, session)
            # If not a season, sort alphabetically at the end
            return (999, session)
        
        return sorted(sessions, key=sort_key)

    def format_output(self, sessions, stats, format_type, courses_analyzed, show_stats):
        """Format the output based on the requested format"""
        
        output = []
        
        # Header info
        output.append(f"📊 Analysis complete!")
        output.append(f"   • Courses analyzed: {courses_analyzed}")
        output.append(f"   • Unique sessions found: {len(sessions)}\n")
        
        if format_type == 'list':
            output.append("📋 Unique Sessions:")
            for i, session in enumerate(sessions, 1):
                count = stats.get(session, 0)
                output.append(f"   {i:2}. {session} (used in {count} courses)")
                
        elif format_type == 'json':
            output.append("📄 JSON Format:")
            output.append(json.dumps(sessions, indent=2))
            
        elif format_type == 'choices':
            output.append("🐍 Django Choices Format:")
            output.append("SESSION_CHOICES = [")
            for session in sessions:
                # Create a nice label from the session name
                label = session.replace('_', ' ').title()
                output.append(f"    ('{session}', '{label}'),")
            output.append("]")
            
        elif format_type == 'sql':
            output.append("📊 SQL Update Statements:")
            output.append("-- You can use these to standardize session names if needed")
            for session in sessions:
                output.append(f"-- Sessions containing '{session}': {stats.get(session, 0)} courses")
        
        if show_stats:
            output.append("\n📈 Session Statistics:")
            sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
            for session, count in sorted_stats:
                percentage = (count / courses_analyzed) * 100
                output.append(f"   • {session}: {count} courses ({percentage:.1f}%)")
        
        output.append("\n" + "="*50)
        output.append("💡 Suggestions:")
        output.append("   • Use --format=choices to get Django choices format")
        output.append("   • Use --show-stats to see usage statistics")
        output.append("   • Use --save-to-file to save results")
        
        return '\n'.join(output)
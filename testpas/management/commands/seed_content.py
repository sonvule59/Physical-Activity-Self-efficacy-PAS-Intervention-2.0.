from django.core.management.base import BaseCommand
from testpas.models import Content

class Command(BaseCommand):
    help = 'Seeds the database with default website content'

    def handle(self, *args, **kwargs):
        content_data = [
            {
                'content_type': 'exit_screen',
                'title': 'Exit Screen - Not Eligible',
                'content': '''
                    <h2>Thank You for Your Interest</h2>
                    <p>Unfortunately, based on your responses, you are not eligible to participate in this study at this time.</p>
                    <p>If you have any questions or would like to know more about future opportunities, please contact:</p>
                    <p><strong>Seungmin Lee</strong><br>
                    Principal Investigator<br>
                    Email: svu23@iastate.edu<br>
                    Phone: 517-898-0020</p>
                '''
            },
            {
                'content_type': 'waiting_screen',
                'title': 'Waiting Screen - Enrollment Complete',
                'content': '''
                    <h2>Your Participation is Important to Us</h2>
                    <p>We have received your consent and are processing your enrollment. Please wait while we finalize the details. You will be contacted by our research team soon.</p>
                    <p>If you have any questions in the meantime, please contact:</p>
                    <p><strong>Seungmin Lee</strong><br>
                    Principal Investigator<br>
                    Email: svu23@iastate.edu<br>
                    Phone: 517-898-0020</p>
                '''
            },
            {
                'content_type': 'consent_form',
                'title': 'Consent Form',
                'content': '''
                    <h2>Consent to Participate</h2>
                    <p>Please read the following information and provide your consent to participate in this study.</p>
                    <p>By consenting to participate, you agree to comply with the study requirements, including:</p>
                    <ul>
                        <li>Wearing a physical activity monitor for two weeks during the study (e.g., one week at the beginning and one week at the end).</li>
                        <li>Responding to emails and phone contacts from the research team.</li>
                        <li>Following all instructions related to the study.</li>
                    </ul>
                    <p>If you have any questions about the study, feel free to reach out to the research team.</p>
                '''
            },
            {
                'content_type': 'eligibility_interest',
                'title': 'Eligibility Interest Page',
                'content': '''
                    <h2>Are you interested in participating in the eligibility questionnaire?</h2>
                    <p>This questionnaire will take approximately 1-2 minutes to complete and will help us determine if you are eligible to participate in our study.</p>
                '''
            },
            {
                'content_type': 'home_page',
                'title': 'Home Page Content',
                'content': '''
                    <h1>Welcome to PAS 2.0!</h1>
                    <p>Thank you for your interest in the Physical Activity Self-efficacy (PAS) Intervention 2.0 study.</p>
                    <p>For assistance, contact Seungmin ("Seung") Lee at svu23@iastate.edu or 517-898-0020.</p>
                '''
            }
        ]
        
        for content_item in content_data:
            obj, created = Content.objects.get_or_create(
                content_type=content_item['content_type'],
                defaults={
                    'title': content_item['title'],
                    'content': content_item['content']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created content: {content_item['title']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Content already exists: {content_item['title']}"))
        
        self.stdout.write(self.style.SUCCESS("Content seeding complete")) 
# Physical Activity Self-efficacy (PAS) Intervention 2.0

A Django-based web application for managing a research study on physical activity interventions. This system handles participant enrollment, eligibility screening, randomization, survey distribution, and physical activity monitoring across multiple waves.

## Overview

The PAS Intervention 2.0 is a comprehensive research platform that:
- Manages participant registration and eligibility screening
- Implements double-blind randomization for control and intervention groups
- Automates email communications throughout the study timeline
- Tracks physical activity monitoring across multiple waves
- Handles survey distribution and data collection
- Manages incentive tracking (Amazon gift cards)

## Study Timeline

The study follows a 112-day timeline from enrollment:
- **Day 1**: Enrollment and Wave 1 Survey
- **Days 11-20**: Wave 1 Physical Activity Monitoring
- **Day 29**: Randomization (Control vs Intervention groups)
- **Days 29-56**: Intervention access for treatment group
- **Day 57**: Wave 2 Survey
- **Day 85**: Wave 3 Survey
- **Days 95-104**: Wave 3 Physical Activity Monitoring
- **Day 112**: Study completion

## Key Features

### 1. Participant Management
- Secure registration with access code
- Email verification system
- Password reset functionality
- Eligibility screening (age, BMI, device access, etc.)

### 2. Study Groups
- **Group 0 (Control)**: Receives intervention access after study completion
- **Group 1 (Intervention)**: Immediate intervention access for 4 weeks

### 3. Automated Communications
- 25 different email templates
- Scheduled email delivery based on enrollment date
- SMS notification capability (optional)
- Customizable email content through admin interface

### 4. Data Collection
- Online survey sets at Waves 1, 2, and 3
- Physical activity monitoring at Waves 1 and 3
- Daily activity logs
- Intervention engagement tracking

### 5. Incentive System
- $5 per survey completion (3 surveys)
- $35 for Wave 1 activity monitoring
- $40 for Wave 3 activity monitoring
- $20 for completing 24+ intervention challenges
- Total possible: $90 in Amazon gift cards

## Technical Requirements

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL 12+ (recommended) or MySQL 8.0+
- Redis (for Celery task queue)
- Email server (SMTP)
- SMS gateway (optional)

### Python Dependencies
```
Django==4.2.0
celery==5.3.0
django-celery-beat==2.5.0
psycopg2-binary==2.9.6
redis==4.5.0
django-crispy-forms==2.0
django-environ==0.10.0
Pillow==9.5.0
boto3==1.26.0  # For AWS SES email
twilio==8.2.0  # For SMS (optional)
pandas==2.0.0  # For data export
openpyxl==3.1.0  # For Excel export
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pas-intervention
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
pas_intervention/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── pas_intervention/          # Main project directory
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── accounts/             # User authentication & registration
│   ├── eligibility/          # Eligibility screening
│   ├── surveys/              # Survey management
│   ├── monitoring/           # Physical activity monitoring
│   ├── interventions/        # Intervention content & tracking
│   ├── communications/       # Email/SMS management
│   ├── randomization/        # Study group assignment
│   └── reports/              # Data export & reporting
├── templates/                # HTML templates
├── static/                   # CSS, JS, images
├── media/                    # User-uploaded files
└── locale/                   # Internationalization files
```

## Configuration

### Email Settings
Configure email settings in `.env`:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Celery Configuration
For scheduled tasks (email sending):
```bash
# Start Celery worker
celery -A pas_intervention worker -l info

# Start Celery beat scheduler
celery -A pas_intervention beat -l info
```

### Admin Interface
Access the admin interface at `/admin/` to:
- View and manage participants
- Edit email templates
- Monitor study progress
- Export data
- Configure study parameters

## Testing

### Run tests
```bash
python manage.py test
```

### Test with compressed timeline
The system supports a compressed timeline for testing (112 minutes instead of 112 days):
```bash
python manage.py test --settings=pas_intervention.settings.test
```

## Data Export

Data can be exported through the admin interface in Excel format, including:
- Participant registration data
- Eligibility screening results
- Survey responses
- Activity monitoring data
- Randomization results
- Intervention engagement metrics

## Security Considerations

- All passwords are hashed using Django's default PBKDF2 algorithm
- Session security with HTTPS enforcement in production
- CSRF protection enabled
- Email verification required for account activation
- Secure random token generation for password resets
- Data access restricted by user roles

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure allowed hosts
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database
- [ ] Set up email service (AWS SES recommended)
- [ ] Configure static file serving
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Test disaster recovery procedures

### Recommended Deployment Stack
- **Web Server**: Nginx
- **Application Server**: Gunicorn
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery with Redis
- **Monitoring**: Sentry
- **Hosting**: AWS EC2 or DigitalOcean

## Maintenance

### Daily Tasks
- Monitor email delivery status
- Check for failed Celery tasks
- Review error logs

### Weekly Tasks
- Database backups
- Review participant progress
- Generate progress reports

### End of Study
- Export all data
- Generate final reports
- Archive study data
- Distribute remaining incentives

## Support

For technical support or questions about the system:
- **Principal Investigator**: Seungmin ("Seung") Lee
- **Email**: svu23@iastate.edu
- **Phone**: 517-898-0020

## License

This project is proprietary software for research purposes. All rights reserved.

## Acknowledgments

Developed for the Obesity and Physical Activity Research Team at Iowa State University.
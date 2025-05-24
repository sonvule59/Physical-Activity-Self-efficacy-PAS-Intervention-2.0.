# PAS Intervention 2.0 - Setup and Implementation Guide

## Overview

This guide explains how the Django application implements all 26 information requirements from the PAS Intervention 2.0 document. The system manages a 112-day research study with participant enrollment, surveys, physical activity monitoring, and intervention delivery.

## Key Implementation Details

### 1. Project Structure

The application is built on your existing Django project (`testpas`) with enhanced models, views, and automated email scheduling.

```
config/                 # Main project configuration
├── settings.py        # Updated settings with all requirements
├── urls.py           # Main URL configuration
└── celery.py         # Celery configuration for scheduled tasks

testpas/              # Your existing app, enhanced
├── models.py         # Updated models for all requirements
├── views.py          # Views for all 26 information points
├── forms.py          # Your existing forms (compatible)
├── tasks.py          # NEW: Celery tasks for automated emails
├── urls.py           # NEW: App-specific URLs
└── migrations/       # Including email template data
```

### 2. Database Models

The updated models maintain compatibility with your existing code while adding:

- **CustomUser**: Extended AbstractUser with study-specific fields
- **Participant**: Maintains your existing structure with additional tracking
- **EmailTemplate**: Stores all 15 email templates (editable by admin)
- **EmailLog**: Tracks all sent emails
- **UserSurveyProgress**: Enhanced progress tracking

### 3. Study Timeline Implementation

The 112-day timeline is automatically managed:

| Day | Action | Information # |
|-----|--------|---------------|
| 1 | Enrollment & Wave 1 Survey email | 9 |
| 11 | Wave 1 Monitoring email | 10 |
| 11-20 | Code entry window (Wave 1) | 11 |
| Code+8 | Return monitor email | 13 |
| 21 | Missing code email (if applicable) | 14 |
| 29 | Randomization & group emails | 15, 16, 17 |
| 57 | Wave 2 Survey email | 18 |
| 67 | No Wave 2 Monitoring email | 19 |
| 85 | Wave 3 Survey email | 20 |
| 95 | Wave 3 Monitoring email | 21 |
| 95-104 | Code entry window (Wave 3) | 22 |
| Code+8 | Study end email | 24 |
| 105 | Missing code email (if applicable) | 25 |

### 4. Email Automation

Emails are sent automatically using Celery Beat:
- Checks every 5 minutes for emails to send
- Tracks what has been sent to avoid duplicates
- All emails CC to `svu23@iastate.edu` as specified
- Templates are customizable through Django admin

### 5. Key Features Implemented

#### Information 1: Website Information
- Site name: "Physical Activity Self-efficacy (PAS) Intervention 2.0"
- Invitation-only access via registration code

#### Information 2: Create Your Account
- Registration code: `wavepa` (case-insensitive)
- Required fields: ID, password, email, phone
- Optional: Full name

#### Information 3: Email Confirmation
- Automatic email with confirmation link
- Account activation required before login

#### Information 4-6: Screening Process
- Interest determination
- Eligibility criteria (age 18-64, BMI ≥25, etc.)
- IRB consent form

#### Information 7-8: Exit/Waiting Screens
- Appropriate messaging for ineligible/declined participants
- Waiting screen for enrolled participants

#### Information 15: Randomization
- Automatic on Day 29 at 7 AM CT
- Equal chance for Group 0 (control) or Group 1 (intervention)

#### Information 26: Data Export
- Admin interface for data download
- Compressed timeline testing (112 minutes instead of days)

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Initialize Email Templates
```bash
python manage.py initialize_email_templates
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Start Services

#### Development:
```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A config worker -l info

# Terminal 3: Celery Beat
celery -A config beat -l info

# Terminal 4: Redis (if not already running)
redis-server
```

### 7. Testing with Compressed Timeline

Create a test participant:
```bash
python manage.py setup_test_participant --username testuser --email test@example.com
```

Run compressed timeline (1 day = 1 second):
```bash
python manage.py test_timeline --participant-id P001 --speed 1
```

## Admin Interface

Access `/admin/` to:
- View and edit email templates
- Monitor participant progress
- Export data (Information 26)
- View email logs
- Manage randomization

## Integration with Existing Code

Your existing code remains functional with these updates:
- `Participant` model enhanced but backward compatible
- `CustomUser` replaces `User` but maintains same functionality
- Email sending methods (`send_wave1_survey_email`, etc.) now use templates
- Forms continue to work as before

## Production Deployment

1. Set `DEBUG = False` in production
2. Configure proper email backend (not console)
3. Set up SSL certificates
4. Configure production database
5. Use a process manager for Celery
6. Set up monitoring and backups

## Troubleshooting

### Emails not sending:
- Check Celery is running
- Verify email configuration in `.env`
- Check `EmailLog` in admin for errors

### Participant not progressing:
- Verify enrollment_date is set
- Check current study day in admin
- Review Celery logs

### Compressed timeline issues:
- Ensure `TEST_MODE = True` only during testing
- Check `TEST_TIME_SCALE` setting
- Monitor Celery worker output

## Next Steps

1. Customize email templates in admin as needed
2. Implement survey questions and data collection
3. Build intervention content and challenge tracking
4. Set up data export formats
5. Configure production email service (AWS SES recommended)
6. Test full 112-day cycle with compressed timeline

This implementation provides a complete framework for the PAS Intervention 2.0 study while maintaining compatibility with your existing code structure.
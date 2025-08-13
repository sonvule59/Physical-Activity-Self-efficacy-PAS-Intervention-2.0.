# PAS Intervention 2.0 - Testing Guide

## 🚀 Quick Start Testing with Time Compression

### Time Compression Setup
- **Current Setting**: 10 seconds = 1 study day
- **Full Study Duration**: 112 days = ~18.7 minutes
- **Key Milestones**:
  - Day 1 (Enrollment): 0 seconds
  - Day 11 (Wave 1 Monitoring): 100 seconds (1.7 minutes)
  - Day 21 (Wave 1 End): 200 seconds (3.3 minutes)
  - Day 29 (Randomization): 280 seconds (4.7 minutes)
  - Day 57 (Wave 2 Survey): 560 seconds (9.3 minutes)
  - Day 85 (Wave 3 Survey): 840 seconds (14 minutes)
  - Day 95 (Wave 3 Monitoring): 940 seconds (15.7 minutes)
  - Day 105 (Study End): 1040 seconds (17.3 minutes)

## 📋 Step-by-Step Testing Process

### 1. **Initial Setup**
```bash
# Run migrations for new features
python manage.py makemigrations
python manage.py migrate

# Seed initial data
python manage.py seed_email_template
python manage.py seed_content
python manage.py seed_eligibility_survey
```

### 2. **Start the Development Server**
```bash
python manage.py runserver
```

### 3. **Start Celery for Email Automation**
```bash
# In a new terminal
celery -A config worker -l info
```

### 4. **Start Celery Beat for Scheduled Tasks**
```bash
# In another terminal
celery -A config beat -l info
```

## 🧪 Participant Journey Testing

### **Phase 1: Account Creation (0-10 seconds)**
1. Go to `http://127.0.0.1:8000/`
2. Click "Create Account"
3. Fill out the form:
   - **Full Name**: Test Participant
   - **ID**: testuser123
   - **Password**: testpass123
   - **Password Confirmation**: testpass123
   - **Email**: test@example.com
   - **Phone**: 555-123-4567
   - **Registration Code**: wavepa
4. Submit and check email for confirmation
5. Click confirmation link

### **Phase 2: Eligibility Interest (10-20 seconds)**
1. Should redirect to interest questionnaire
2. Select "Interested"
3. Submit

### **Phase 3: Eligibility Criteria (20-30 seconds)**
1. Fill out eligibility form:
   - **Age**: 25
   - **Height**: 70 inches
   - **Weight**: 180 lbs
   - **Device Access**: Yes
   - **No Other Studies**: Yes
   - **Monitoring**: Yes
   - **Contact**: Yes
2. Submit (should be eligible with BMI = 25.8)

### **Phase 4: Consent (30-40 seconds)**
1. Read consent form
2. Select "I consent to participate"
3. Submit

### **Phase 5: Waiting Period (40-100 seconds)**
- Should see waiting screen
- Wait for Day 11 (100 seconds total)

### **Phase 6: Wave 1 Monitoring (100-200 seconds)**
1. At 100 seconds, check email for Wave 1 monitoring email
2. Go to dashboard
3. Should see Wave 1 code entry available
4. Enter code: "wavepa"
5. Should receive code entry confirmation email

### **Phase 7: Randomization (280 seconds)**
1. At 280 seconds, participant should be randomized
2. Check email for group assignment
3. Group 1: Immediate intervention access
4. Group 0: Later intervention access

### **Phase 8: Intervention Access (280-560 seconds for Group 1)**
1. If Group 1, intervention access should be available
2. Go to `/intervention/` to test access
3. Test progress tracking

### **Phase 9: Wave 2 Survey (560 seconds)**
1. At 560 seconds, check email for Wave 2 survey
2. Should receive survey email

### **Phase 10: Wave 3 Survey (840 seconds)**
1. At 840 seconds, check email for Wave 3 survey
2. Should receive survey email

### **Phase 11: Wave 3 Monitoring (940-1040 seconds)**
1. At 940 seconds, check email for Wave 3 monitoring
2. Go to dashboard
3. Should see Wave 3 code entry available
4. Enter code: "wavepa"
5. Should receive code entry confirmation email

### **Phase 12: Study End (1040+ seconds)**
1. At 1040 seconds, check email for study end
2. Should receive final survey and monitor return email

## 🔧 Testing Tools

### **Time Control Panel**
- Go to `http://127.0.0.1:8000/dev/time-controls/`
- Use to manually advance time for testing

### **Admin Interface**
- Go to `http://127.0.0.1:8000/admin/`
- Monitor participant progress
- Edit email templates and content

### **Compressed Timeline Test**
```bash
# Test timeline progression
python manage.py test_compressed_timeline --days 5 --participant P001
```

## 📊 What to Monitor

### **Email Automation**
- Check email logs in admin
- Verify emails are sent at correct times
- Confirm email content is correct

### **Timeline Progression**
- Monitor study day calculation
- Verify code entry windows open/close correctly
- Check intervention access timing

### **Data Integrity**
- Verify participant data is saved correctly
- Check progress tracking
- Confirm randomization works

## 🐛 Common Issues & Solutions

### **Emails Not Sending**
- Check Celery worker is running
- Verify email settings in settings.py
- Check email templates are seeded

### **Timeline Not Advancing**
- Verify TIME_COMPRESSION = True
- Check SECONDS_PER_DAY = 10
- Restart Celery beat

### **Code Entry Not Available**
- Check study day calculation
- Verify participant has proper progress record
- Check day_1 is set correctly

## 📝 Testing Checklist

- [ ] Account creation with registration code
- [ ] Email confirmation
- [ ] Eligibility questionnaire
- [ ] Consent form
- [ ] Wave 1 code entry (Day 11-20)
- [ ] Randomization (Day 29)
- [ ] Intervention access (Group 1: Day 29-56)
- [ ] Wave 2 survey email (Day 57)
- [ ] Wave 3 survey email (Day 85)
- [ ] Wave 3 code entry (Day 95-104)
- [ ] Study end email (Day 105+)
- [ ] Admin content editing
- [ ] Password reset functionality

## ⏱️ Time Compression Reference

| Study Day | Real Time | Event |
|-----------|-----------|-------|
| 1 | 0s | Enrollment |
| 11 | 100s | Wave 1 Monitoring |
| 21 | 200s | Wave 1 End |
| 29 | 280s | Randomization |
| 57 | 560s | Wave 2 Survey |
| 85 | 840s | Wave 3 Survey |
| 95 | 940s | Wave 3 Monitoring |
| 105 | 1040s | Study End |
| 112 | 1110s | Study Complete |

**Total Testing Time**: ~18.5 minutes for full 112-day study 
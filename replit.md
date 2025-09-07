# ChamaSpace (Chamabora) - Project Documentation

## Overview
ChamaSpace (branded as Chamabora) is a Django-based web application for managing Chama groups - traditional savings and loan associations popular in East Africa. The platform provides features for group management, contributions, loans, investments, and financial tracking.

## Project Architecture

### Backend Framework
- **Django 3.2.18** - Main web framework
- **Python 3.11** - Programming language
- **SQLite** - Database (development), PostgreSQL (production)
- **Gunicorn** - WSGI server for production

### Key Django Apps
- `chamas` - Core Chama group management
- `authentication` - User authentication and profiles
- `Dashboard` - Main dashboard functionality
- `mpesa_integration` - M-Pesa payment integration
- `notifications` - Push notifications (FCM)
- `pyment_withdraw` - Payment withdrawals
- `Goals` - Group goals and activities
- `subscriptions` - Subscription management
- `bot` - Telegram/WhatsApp bot integration

### External Integrations
- **Cloudinary** - Image storage and management
- **Firebase/FCM** - Push notifications
- **Twilio** - SMS messaging
- **M-Pesa** - Mobile payment integration
- **Stripe** - Payment processing

## Development Setup

### Dependencies
All Python dependencies are managed via requirements.txt. Key packages:
- Django 3.2.18
- django-environ (environment variables)
- psycopg2-binary (PostgreSQL adapter)
- cloudinary & django-cloudinary-storage
- firebase-admin & fcm-django
- twilio & django-twilio
- stripe (payment processing)

### Database
- **Development**: SQLite database (db.sqlite3)
- **Production**: PostgreSQL via DATABASE_URL environment variable
- All migrations are up to date and applied

### Static Files
- Managed by WhiteNoise in production
- Static files served from `/static/` directory
- Includes Bootstrap, FontAwesome, custom CSS/JS

### Environment Variables
The application uses django-environ for configuration:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True for development)
- Database credentials (for production)
- API keys for external services (Cloudinary, Twilio, etc.)

## Deployment Configuration

### Development Server
- Runs on `0.0.0.0:5000` (required for Replit environment)
- Command: `python manage.py runserver 0.0.0.0:5000`
- ALLOWED_HOSTS set to `['*']` for proxy compatibility

### Production Deployment
- Uses Gunicorn WSGI server
- Configured for autoscale deployment
- Command: `gunicorn --bind=0.0.0.0:5000 --reuse-port Chamabora.wsgi:application`

## Recent Changes
- September 7, 2025: Initial import and setup in Replit environment
  - Installed Python 3.11 and all required dependencies
  - Applied all Django migrations successfully
  - Configured development server for Replit proxy compatibility
  - Set up production deployment configuration
  - Verified application loads and serves static files correctly

## Current State
- ✅ Application fully functional in development mode
- ✅ Database migrations applied
- ✅ Static files loading correctly
- ✅ Production deployment configured
- ⚠️ Minor JavaScript console warnings (Bootstrap/jQuery load order)

## User Preferences
- None documented yet

## Notes
- The application includes comprehensive Chama management features
- Multiple payment integrations suggest this is production-ready software
- Rich admin interface via django-jazzmin
- Extensive notification system with multiple channels
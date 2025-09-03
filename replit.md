# ChamaBora - Chama Management System

## Project Overview
ChamaBora is a comprehensive Django-based web application for managing Chama (savings groups) activities. It provides features for group financial management, savings tracking, loans, contributions, and member management.

## Architecture
- **Framework**: Django 3.2.18
- **Database**: SQLite (development), supports PostgreSQL for production
- **Frontend**: Bootstrap, HTML/CSS/JavaScript
- **Authentication**: Custom user authentication with OTP support
- **Integrations**: M-Pesa, Twilio, Firebase Cloud Messaging, Cloudinary
- **Languages**: Python 3.11

## Key Features
- User registration and authentication
- Chama (group) creation and management
- Member management and roles
- Contribution tracking and management
- Loan management system
- Financial reporting and analytics
- Notification system (SMS, Push notifications)
- Mobile money integration (M-Pesa)
- Document management
- Goal setting and tracking
- Subscription management

## Project Structure
- `authentication/` - User authentication and profile management
- `chamas/` - Core chama management functionality
- `Dashboard/` - Main dashboard and analytics
- `Goals/` - Personal and group goal management
- `notifications/` - Notification system
- `mpesa_integration/` - M-Pesa payment integration
- `pyment_withdraw/` - Payment withdrawal functionality
- `subscriptions/` - Subscription and payment plans
- `wallet/` - Wallet and financial management
- `home/` - Landing pages and static content
- `bot/` - Bot integration for automated interactions

## Recent Changes
- **2025-09-03**: Successfully imported from GitHub and configured for Replit environment
- Set up Python 3.11 environment with all required dependencies
- Configured Django settings for Replit hosting
- Successfully ran database migrations
- Configured workflow for development server on port 5000
- Static files properly collected and served

## User Preferences
- Development server runs on 0.0.0.0:5000 for Replit compatibility
- Uses SQLite for development database
- Static files managed through WhiteNoise middleware
- CSRF trusted origins configured for Replit domains

## Development Setup
The project is configured to run in the Replit environment with:
- Python 3.11 runtime
- Django development server on port 5000
- All dependencies installed via pip
- Database migrations applied
- Static files collected

## Environment Variables
The project uses placeholder values for development:
- SECRET_KEY: Temporary development key
- TWILIO_*: Placeholder Twilio credentials
- CLOUDINARY_*: Placeholder Cloudinary credentials
- CONSUMER_KEY/SECRET: Placeholder M-Pesa credentials

## Next Steps
- Replace placeholder API keys with actual credentials when deploying
- Configure production database settings
- Set up proper security settings for production deployment
- Configure HTTPS and security headers for production

## Dependencies
All Python dependencies are managed through requirements.txt and include:
- Django 3.2.18
- Various Django extensions (django-twilio, fcm-django, etc.)
- Third-party integrations (cloudinary, twilio, stripe, etc.)
- PDF generation libraries (reportlab, xhtml2pdf)
- Authentication libraries (firebase-admin, pyfcm)
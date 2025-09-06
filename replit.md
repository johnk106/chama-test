# ChamaSpace - Chama Management Platform

## Overview
ChamaSpace (Chamabora) is a Django-based web application for managing chama (group savings) activities. It provides features for group management, contributions tracking, loans, investments, and financial reporting.

## Recent Changes (September 6, 2025)
- Successfully imported from GitHub and configured for Replit environment
- Installed Python 3.11 and all required Django dependencies
- Configured Django settings to work without .env file using environment defaults
- Fixed M-Pesa integration API call issues during startup
- Set up SQLite database for development and ran all migrations  
- Collected static files and configured proper static file serving
- Updated workflow to serve Django development server on port 5000
- Set up deployment configuration using autoscale with Gunicorn
- **Application now fully functional**: Landing page loads correctly with all styling and assets

## Project Architecture

### Core Apps
- **authentication**: User registration, login, and profile management
- **chamas**: Core chama functionality, members, contributions, loans, fines
- **Dashboard**: Main dashboard and analytics
- **Goals**: Savings goals and financial targets
- **notifications**: Push notifications using FCM
- **wallet**: Digital wallet and payment processing
- **subscriptions**: Subscription plans and billing
- **mpesa_integration**: M-Pesa mobile payment integration
- **pyment_withdraw**: Withdrawal and payout functionality

### Key Features
- Group savings management (chamas)
- Member contributions tracking
- Loan management with due dates and interest
- Fine and penalty system
- Investment and income tracking
- Mobile money integration (M-Pesa)
- Push notifications
- PDF report generation
- Subscription billing

### Tech Stack
- **Backend**: Django 3.2.18
- **Database**: SQLite (development), PostgreSQL support available
- **Frontend**: Bootstrap, jQuery, Swiper.js
- **Payment**: Stripe, M-Pesa integration
- **Cloud Storage**: Cloudinary
- **Notifications**: Firebase FCM
- **PDF Generation**: ReportLab, xhtml2pdf
- **Server**: Gunicorn for production

## Development Setup
- Python 3.11 with dependencies from requirements_clean.txt
- Django development server runs on port 5000
- Database: SQLite (db.sqlite3)
- Static files served via Whitenoise
- CSRF protection configured for Replit domains

## Deployment
- Target: Replit Autoscale
- Build: Install dependencies from requirements_clean.txt
- Run: Gunicorn WSGI server on port 5000
- Production-ready with proper static file handling

## Environment Variables
The application uses placeholder values for development. For production:
- Twilio credentials for SMS
- Cloudinary for media storage
- M-Pesa API credentials
- Firebase FCM server key
- Stripe payment keys

## Status
✅ Application successfully running in Replit environment
✅ All core functionality accessible
✅ Database migrations completed
✅ Static files loading correctly
✅ Deployment configuration ready
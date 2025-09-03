# Overview

Chamabora is a comprehensive Django-based financial platform designed to facilitate community-based savings groups (chamas) in Kenya. The platform integrates traditional chama (rotating credit association) management with modern digital financial services, including M-Pesa integration, goal-based savings, peer-to-peer transactions, and automated SMS/push notifications. It serves as a complete fintech solution for organizing, managing, and tracking group savings activities while providing individual financial management tools.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Django 3.1+**: Core web framework providing MVC architecture, ORM, and admin interface
- **Python**: Primary programming language for business logic and integrations
- **SQLite/PostgreSQL**: Database layer using Django ORM with multiple models for financial data
- **ASGI/WSGI**: Application servers for handling HTTP requests and WebSocket connections

## Authentication & User Management
- **Django Auth System**: Built-in user authentication with custom Profile model extensions
- **Phone-based Authentication**: OTP verification system using SMS for user registration
- **Role-based Access Control**: Custom role system for chama membership hierarchy (admin, treasurer, member)
- **Session Management**: Django sessions with custom middleware for subscription validation

## Financial Services Integration
- **M-Pesa Integration**: Real-time mobile money transactions using Safaricom's API
- **Twilio SMS**: Automated notifications and OTP delivery
- **Payment Processing**: STK Push implementation for seamless mobile payments
- **Transaction Tracking**: Comprehensive audit trail for all financial activities

## Core Business Logic
- **Chama Management**: Complete lifecycle management of rotating savings groups
- **Contribution Tracking**: Automated contribution cycles (daily, weekly, bi-weekly, monthly)
- **Award Distribution**: Algorithmic payout scheduling based on contribution turns
- **Fine System**: Automated penalty calculation for late payments
- **Loan Management**: Internal lending with interest calculation and payment tracking

## Savings & Goals System
- **Personal Goals**: Individual savings targets with automated reminders
- **Group Goals**: Collaborative savings with member contribution tracking
- **Express Savings**: Quick deposit system with interest calculations
- **Interest Calculations**: Compound interest using date-based calculations

## Notification System
- **Firebase Cloud Messaging**: Push notifications for mobile app users
- **SMS Notifications**: Twilio-based messaging for contribution reminders and alerts
- **Email Notifications**: Django email system for administrative communications
- **Real-time Updates**: WebSocket connections for live dashboard updates

## Bot Integration
- **WhatsApp/SMS Bot**: Automated message processing for contribution confirmations
- **Natural Language Processing**: Message parsing for financial transaction data
- **Fraud Detection**: Pattern recognition for suspicious transaction activities
- **Automated Approvals**: Rule-based transaction validation system

## Subscription Management
- **Tiered Subscriptions**: Multiple pricing plans with feature restrictions
- **Trial Periods**: Free trial implementation with automatic conversion
- **Payment Integration**: M-Pesa subscription billing with webhook callbacks
- **Access Control**: Middleware-based feature gating based on subscription status

## Data Architecture
- **Multi-app Structure**: Modular Django apps (authentication, dashboard, goals, chamas, etc.)
- **Related Models**: Complex foreign key relationships for financial data integrity
- **Audit Logging**: Timestamp tracking for all financial transactions
- **Data Validation**: Model-level constraints ensuring data consistency

## Security Features
- **CSRF Protection**: Django's built-in CSRF middleware
- **Input Sanitization**: Form validation and data cleaning
- **Access Control**: Function decorators for permission checking
- **Secure Payment Processing**: Encrypted API communications with financial providers

# External Dependencies

## Financial Service Providers
- **Safaricom M-Pesa API**: Mobile money integration for payments and withdrawals
- **M-Pesa STK Push**: Real-time payment initiation service
- **M-Pesa C2B**: Customer-to-business payment callbacks

## Communication Services
- **Twilio**: SMS delivery for notifications and OTP verification
- **Firebase**: Push notification delivery and user engagement tracking
- **Infobip**: SMS gateway for bot message processing

## Infrastructure Services
- **Cloudinary**: Image and media file storage for user profiles and documents
- **Django Static Files**: Local static asset management
- **Session Storage**: Django's database-backed session management

## Frontend Technologies
- **Firebase SDK**: Client-side push notification handling
- **JavaScript**: Frontend interactivity and API communications
- **HTML/CSS**: Template rendering with Django's template system

## Development Tools
- **Django Admin**: Administrative interface for data management
- **Django Migrations**: Database schema version control
- **Python Package Management**: Requirements-based dependency management
- **Environment Configuration**: Settings management for different deployment stages

## Monitoring & Analytics
- **Transaction Logging**: Custom logging for financial operations
- **User Activity Tracking**: Session-based user behavior monitoring
- **Error Handling**: Django's exception handling with custom error pages
- **Performance Monitoring**: Database query optimization and caching strategies
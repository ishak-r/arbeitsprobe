# License Management Module for Odoo 19

## Description

This module allows you to manage software licenses for your customers in
Odoo 19. It provides a complete solution to create, track, and renew software
licenses.

## Features

### 1. License Management

-   Automatic generation of unique license numbers (format: LIC-00001)
-   Automatic generation of license keys (format: XXXX-XXXX-XXXX-XXXX)
-   License status tracking (Draft, Active, Expired, Suspended, Canceled)
-   Management of start and expiration dates

### 2. Product Extension

-   Mark products as "Is a License"
-   Quick access to licenses related to a product

### 3. Customer/Partner Extension

-   Overview of licenses per customer
-   Quick access to a customer's licenses

### 4. Automation

-   Daily scheduled action: Automatically updates expired license status
-   Daily scheduled action: Automatically sends reminder emails 7 days before expiration
-   Automatic calculation of expiration date based on duration

### 5. User Interface

-   List and Form views for licenses
-   Smart filters and grouping options
-   Visual indicators (colors) for active, expired, or soon-to-expire licenses
-   Smart buttons on products and partners

### 6. Email Notifications

-   Professional email template for expiration reminders
-   Automatic sending to customers 7 days before expiration
-   Detailed license information included in the email

## Installation

1.  Copy the `license_management` folder into your Odoo addons directory
2.  Restart the Odoo server
3.  Go to Apps \> Update Apps List
4.  Search for "License Management"
5.  Click "Install"

## Configuration

### Security Groups

The module creates two groups: 
- **User**: Can create and modify licenses 
- **Manager**: Full access, including deleting licenses

### Scheduled Actions

Two scheduled actions are created automatically: 
1. **Expired License Check**: Runs daily to update license status 
2. **Expiration Reminder Emails**: Runs daily to send reminder emails

These actions can be configured in: Settings \> Technical \> Automation \> Scheduled Actions

## Usage

### Create a License Product

1.  Go to License Management \> Products
2.  Create or edit a product
3.  Check "Is a License"

### Create a License

1.  Go to License Management \> Licenses \> All Licenses
2.  Click "Create"
3.  Select the product and customer
4.  Set the start date and duration
5.  The expiration date and license key are generated automatically
6.  Click "Activate" to activate the license

### Renew a License

1.  Open an active license
2.  Click "Renew"
3.  Set the duration in the wizard and confirm
4.  The license will be extended automatically

### View Customer Licenses

1.  Open a customer form
2.  Click the "Licenses" smart button

## File Structure

    license_management/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init __.py
    │   ├── software_license.py
    │   ├── product_template.py
    │   └── res_partner.py
    ├── views/
    │   ├── software_license_views.xml
    │   ├── product_template_views.xml
    │   ├── res_partner_views.xml
    │   └── menu.xml
    ├── security/
    │   ├── license_security.xml
    │   └── ir.model.access.csv    
    ├── wizard/
    │   ├── __init__.py
    │   ├── software_license_renew_wizard_views.xml
    │   └── software_license_renew_wizard.py
    ├── data/
    │   ├── software_license_sequence.xml
    │   ├── license_cron.xml
    │   └── email_template.xml
    ├── i18n/
    │   └── de.po
    └── static/
        └── description/
            └── index.html

## Main License Model Fields

-   `name`: License number (auto-generated)
-   `license_key`: Unique license key (auto-generated)
-   `product_id`: Licensed product
-   `partner_id`: Customer
-   `start_date`: Start date
-   `expiration_date`: Expiration date
-   `duration_months`: Duration in months
-   `state`: Status (draft, active, expired, suspended, canceled)
-   `days_until_expiration`: Remaining days (computed)
-   `is_expiring_soon`: Expiring soon indicator (computed)

## Important Methods

-   `_generate_license_key()`: Generates a unique license key
-   `action_activate()`: Activates a license
-   `action_suspend()`: Suspends a license
-   `action_renew()`: Renews a license
-   `_cron_check_expired_licenses()`: Scheduled action for expired licenses
-   `_cron_send_expiration_reminders()`: Scheduled action for reminder emails

## Dependencies

-   contacts
-   product
-   mail

## Version

-   Module version: 1.0.0
-   Compatible with: Odoo 19.0

## License

LGPL-3

## Possible Future Improvements

-   Customer portal to view licenses
-   License reporting
-   Billing integration
-   Renewal history
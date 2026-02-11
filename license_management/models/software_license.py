from odoo import models, fields, api
from odoo.exceptions import ValidationError
import secrets
import string
from datetime import timedelta


class SoftwareLicense(models.Model):
    _name = 'software.license'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Software License'


    name = fields.Char(
        string='License Number',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        tracking=True
    )
    
    license_key = fields.Char(
        string='License Key',
        copy=False,
        readonly=True,
        tracking=True
    )
    
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        domain="[('is_license', '=', True)]",
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True
    )
    
    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    expiration_date = fields.Date(
        string='Expiration Date',
        tracking=True,
        compute='_compute_expiration_date',
        store=True
    )
    
    state = fields.Selection(
        selection=[('draft', 'Draft'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('suspended', 'Suspended'),
            ('canceled', 'Canceled')], 
        string='State', 
        default='draft', 
        required=True, 
        tracking=True
    )

    duration_months = fields.Integer(
        string='Duration (Months)',
        default=12,
        help='License duration in months'
    )

    notes = fields.Text(string='Notes')
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True)
    
    days_until_expiration = fields.Integer(
        string='Days Until Expiration',
        compute='_compute_days_until_expiration',
        store=False
    )
    
    is_expiring_soon = fields.Boolean(
        string='Expiring Soon',
        compute='_compute_is_expiring_soon',
        store=True,
        help='True if license expires in 7 days or less'
    )

    date_renewed = fields.Date(string='Date Renewed', readonly=True)

    @api.depends('expiration_date')
    def _compute_days_until_expiration(self):
        """Calculate days until expiration"""
        today = fields.Date.today()
        for record in self:
            if record.expiration_date:
                delta = record.expiration_date - today
                record.days_until_expiration = delta.days
            else:
                record.days_until_expiration = 0

    @api.depends('days_until_expiration', 'state')
    def _compute_is_expiring_soon(self):
        """Check if license is expiring soon (within 7 days)"""
        for record in self:
            record.is_expiring_soon = (
                record.state == 'active' and
                0 <= record.days_until_expiration <= 7
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate license number and key"""
        print("Creating software license with values:", vals_list)
        for val in vals_list:

            if val.get('name', 'New') == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('software.license') or 'New'
            
            if not val.get('license_key'):
                val['license_key'] = self._generate_license_key()
            
        return super(SoftwareLicense, self).create(vals_list)

    def _generate_license_key(self):
        """Generate a unique license key Format: XXXX-XXXX-XXXX-XXXX"""
        chars = string.ascii_uppercase + string.digits

        while True:
            key_parts = []
            for _ in range(4):
                part = ''.join(secrets.choice(chars) for _ in range(4))
                key_parts.append(part)
            key = '-'.join(key_parts)

            # Check if key already exists
            if not self.search([('license_key', '=', key)], limit=1):
                return key

    @api.depends('start_date', 'duration_months')
    def _compute_expiration_date(self):
        """Compute expiration date based on start date and duration"""
        for record in self: 
            if record.date_renewed:
                return
            if record.start_date and record.duration_months:
                record.expiration_date = record.start_date + timedelta(days=record.duration_months * 30)
            else:
                record.expiration_date = False

    @api.constrains('start_date', 'expiration_date')
    def _check_dates(self):
        """Validate that expiration date is after start date"""
        for record in self:
            if record.expiration_date and record.start_date:
                if record.expiration_date <= record.start_date:
                    raise ValidationError('Expiration date must be after start date!')

    def action_activate(self):
        """Activate license"""
        self.write({'state': 'active'})

    def action_suspend(self):
        """Suspend license"""
        self.write({'state': 'suspended'})

    def action_cancel(self):
        """Cancel license"""
        self.write({'state': 'canceled'})

    def action_renew(self):
        return {
            'name': 'Renew License',
            'type': 'ir.actions.act_window',
            'res_model': 'software.license.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_license_id': self.id}
        }

        # """Renew license for another period"""
        # for record in self:
        #     new_start = record.expiration_date + timedelta(days=1)
        #     new_expiration = new_start + timedelta(days=record.duration_months * 30)
        #     record.write({
        #         'expiration_date': new_expiration,
        #         'state': 'active'
        #     })

    def action_draft(self):
        """Reset license to draft state"""
        self.write({'state': 'draft'})

    @api.model
    def _cron_check_expired_licenses(self):
        """Scheduled action to update expired licenses"""
        today = fields.Date.today()
        expired_licenses = self.search([
            ('state', '=', 'active'),
            ('expiration_date', '<', today)
        ])
        expired_licenses.write({'state': 'expired'})
        return True

    @api.model
    def _cron_send_expiration_reminders(self):
        """Scheduled action to send expiration reminder emails"""
        today = fields.Date.today()
        warning_date = today + timedelta(days=7)

        expiring_licenses = self.search([
            ('state', '=', 'active'),
            ('expiration_date', '<=', warning_date),
            ('expiration_date', '>=', today)
        ])

        template = self.env.ref('license_management.email_template_license_expiration', raise_if_not_found=False)
        if template:
            for license in expiring_licenses:
                template.send_mail(
                    license.id, 
                    email_values={
                        'email_to': license.partner_id.email or license.partner_id.parent_id.email if license.partner_id.parent_id else None,
                    },
                    force_send=True)

        return True

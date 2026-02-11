from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SoftwareLicenseRenewWizard(models.TransientModel):
    _name = 'software.license.renew.wizard'
    _description = 'Software License Renew Wizard'

    license_id = fields.Many2one(
        'software.license', 
        string='Software License',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )

    duration_months = fields.Integer(
        string='Duration (Months)',
        related='license_id.duration_months',
        readonly=False
    )

    @api.constrains('duration_months')
    def _check_duration_months(self):
        for wizard in self:
            if wizard.duration_months <= 0:
                raise ValidationError('Duration must be a positive integer.')

    def renew_license(self):
        for wizard in self:
            license = wizard.license_id
            new_start = license.expiration_date + timedelta(days=1)
            new_expiration = new_start + timedelta(days=wizard.duration_months * 30)
            license.write({
                'expiration_date': new_expiration,
                'date_renewed': fields.Date.today(),
            })
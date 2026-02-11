from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    license_ids = fields.One2many(
        'software.license',
        'partner_id',
        string='Licenses'
    )
    
    license_count = fields.Integer(
        string='Number of Licenses',
        compute='_compute_license_count'
    )
    
    @api.depends('license_ids', 'license_ids.state')
    def _compute_license_count(self):
        """Count total and active licenses"""
        for partner in self:
            partner.license_count = len(partner.license_ids)

    def action_view_licenses(self):
        """Open licenses for this customer"""
        self.ensure_one()
        return {
            'name': 'Customer Licenses',
            'type': 'ir.actions.act_window',
            'res_model': 'software.license',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

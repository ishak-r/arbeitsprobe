from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    is_license = fields.Boolean(
        string='Is a License',
        default=False,
        help='Check this if this product is a software license'
    )
    
    license_count = fields.Integer(
        string='Number of Licenses',
        compute='_compute_license_count'
    )

    def _compute_license_count(self):
        """Count licenses for this product"""
        for product in self:
            product.license_count = self.env['software.license'].search_count([
                ('product_id', '=', product.id)
            ])

    def action_view_licenses(self):
        """Open licenses for this product"""
        self.ensure_one()
        return {
            'name': 'Licenses',
            'type': 'ir.actions.act_window',
            'res_model': 'software.license',
            'view_mode': 'list,form',
            'domain': [('product_id', '=', self.id)],
            'context': {
                'default_product_id': self.id,
            }
        }

from odoo import api, fields, models


class IrLogging(models.Model):
    _inherit = 'ir.logging'


    new_computed_field = fields.Char(compute='_compute_new_computed_field', store=True)

    @api.depends('level', 'message')
    def _compute_new_computed_field(self):
        # Your custom code to compute the new computed field
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxx")
        pass


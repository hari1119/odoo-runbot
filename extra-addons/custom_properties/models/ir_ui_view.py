from odoo import fields,models


class View(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(selection_add=[('map', "Map"),
                             ('dashboard',"Dashboard"), ('fields_tracker', "Fields Tracker")], string='View Type')

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import time
from odoo.exceptions import UserError

class CpMailConfigurationLine(models.Model):
    _name = 'cp.mail.configuration.line'
    _description = 'Custom Mail Configuration Line'
    #_order = 'id'
    
    header_id = fields.Many2one('cp.mail.configuration', string='Mail Configuration Reference', index=True, required=True, ondelete='cascade')
    
    email = fields.Char(string="Email", copy=False, size=252)
    to_address = fields.Boolean('To')
    cc_address = fields.Boolean('Cc')
    bcc_address = fields.Boolean('Bcc')
    
    status = fields.Selection(related='header_id.status', store=True)






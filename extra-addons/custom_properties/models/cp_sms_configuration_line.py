from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import time
from odoo.exceptions import UserError

class CpSmsConfigurationLine(models.Model):
    _name = 'cp.sms.configuration.line'
    _description = 'Custom Sms Configuration Line'
    #_order = 'id'
    
    header_id = fields.Many2one('cp.sms.configuration', string='Sms Configuration Reference', index=True, required=True, ondelete='cascade')

    name = fields.Char('Name', size=128)
    mobile_no = fields.Char(string='Mobile No', size=15)
    
    status = fields.Selection(related='header_id.status', store=True)






from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import time
from odoo.exceptions import UserError
from collections import Counter

class CpMailQueueLine(models.Model):
    _name = 'cp.mail.queue.line'
    _description = 'Mail Queue Line'
    #_order = 'id'

    header_id = fields.Many2one('cp.mail.queue', string='Mail Queue Reference', index=True, required=True, ondelete='cascade')
    
    attachment = fields.Many2many(
        'ir.attachment',
        string='File',
        ondelete='restrict')
    
    status = fields.Selection(related='header_id.status', store=True)

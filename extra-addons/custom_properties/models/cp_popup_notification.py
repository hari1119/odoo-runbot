
import time
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import Counter
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class CpPopupNotification(models.Model):
    _name = 'cp.popup.notification'
    _description = 'Custom Popup Notification'
    #_order = 'id'

    name = fields.Char('Purpose', index=True, copy=False)
    entry_date = fields.Date(string="Entry Date", copy=False, default=fields.Date.today)
    user_id = fields.Many2one('res.users', string="User Name")
    
    def unlink(self):
        """ Unlink """
        for rec in self:
            models.Model.unlink(rec)
        return True

    def write(self, vals):
        """ write """
        return super(CpPopupNotification, self).write(vals)


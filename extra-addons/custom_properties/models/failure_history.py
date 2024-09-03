from odoo import fields, models


class FailureHistory(models.Model):
    """Creates failure history to store the failed cron action details
        as a record"""
    _name = 'failure.history'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Failure History'

    name = fields.Char(string='Name', required=True, readonly=True, 
                        help="Failed cron action name")
    error = fields.Char(string='Error Details', readonly=True, 
                        help="Detailed description about error")
    crt_date = fields.Datetime(string="Created Date", readonly=True, 
                                copy=False, default=fields.Datetime.now)


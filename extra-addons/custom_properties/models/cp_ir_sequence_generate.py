from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import time
from odoo.exceptions import UserError

ENTRY_MODE =  [('manual','Manual'),
               ('auto', 'Auto')]

class CpIrSequenceGenerate(models.Model):
    _name = 'cp.ir.sequence.generate'
    _description = 'Ir Sequence Generate'
    #_order = 'id'

    name = fields.Char('Name')
    ir_sequence_id = fields.Many2one('ir.sequence', 'Sequence Ref')
    seq_month = fields.Char('Sequence Month')
    seq_year = fields.Char('Sequence Year')
    seq_next_number = fields.Integer('Sequence Next Number')
    fiscal_year_code = fields.Char('Fiscal Year Code', size=5)
    fiscal_year_id = fields.Integer('Fiscal Year ID')
    company_id = fields.Many2one('res.company', 'Company')
    division_id = fields.Many2one('cm.master', 'Division')

    ### Entry Info ###
    entry_mode = fields.Selection(selection=ENTRY_MODE, string="Entry Mode", copy=False, tracking=True, default='manual')
    active = fields.Boolean(string="Visible", default=True)
    user_id = fields.Many2one('res.users', string="Created By", readonly=True, copy=False,
                                    ondelete='restrict', default=lambda self: self.env.user.id)
    crt_date = fields.Datetime(string="Creation Date", readonly=True, copy=False, default=fields.Datetime.now)
    update_user_id = fields.Many2one('res.users', string="Last Update By", readonly=True, copy=False,
                                    ondelete='restrict')
    update_date = fields.Datetime(string="Last Update Date", readonly=True, copy=False)

    @api.constrains('seq_next_number')
    def _check_seq_next_number_size(self):
        for record in self:
            if record.seq_next_number:
                if len(str(record.seq_next_number)) > 5:
                    raise UserError("Sequence Next Number must be at most 5 digits.")
                if record.seq_next_number < 0:
                    raise UserError("Sequence Next Number cannot be a negative number.")

    def write(self, vals):
        """ write """
        vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                     'update_user_id': self.env.user.id})
        return super(CpIrSequenceGenerate, self).write(vals)

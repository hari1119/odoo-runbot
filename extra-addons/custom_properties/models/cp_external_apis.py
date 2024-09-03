
import time
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import Counter
from dateutil.relativedelta import relativedelta
from odoo.addons.custom_properties.decorators import validation,is_special_char,is_special_char_pre_or_suf,is_mobile_num,is_valid_mail

_logger = logging.getLogger(__name__)

CUSTOM_STATUS = [
    ('draft', "Draft"),
    ('editable', 'Editable'),
    ('active', "Active"),
    ('inactive', "Inactive")]

ENTRY_MODE =  [('manual','Manual'),
               ('auto', 'Auto')]

class CpExternalAPIs(models.Model):
    _name = 'cp.external.apis'
    _description = 'Custom External APIs'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'avatar.mixin']
    #_order = 'id'

    name = fields.Char('Purpose', index=True, copy=False)
    status = fields.Selection(selection=CUSTOM_STATUS, string="Status", readonly=True, store=True, copy=False, default='draft')
    api_link = fields.Char('API Link')
    service_provider = fields.Char('Service Provider')
    user_name = fields.Char('User Name')
    password = fields.Char('Password')
    inactive_remark = fields.Text('Inactive Remark')

    ### Entry Info ###
    active = fields.Boolean(string="Visible", default=True)
    active_rpt = fields.Boolean('Visible in Report', default=True)
    active_trans = fields.Boolean('Visible in Transactions', default=True)
    entry_mode = fields.Selection(selection=ENTRY_MODE, string="Entry Mode", readonly=True, copy=False,
                                  tracking=True, default='manual')
    company_id = fields.Many2one('res.company', required=True, copy=False,
                      readonly=True, default=lambda self: self.env.company, ondelete='restrict')
    user_id = fields.Many2one('res.users', string="Created By", readonly=True, copy=False,
                                    ondelete='restrict', default=lambda self: self.env.user.id)
    crt_date = fields.Datetime(string="Creation Date", readonly=True, copy=False, default=fields.Datetime.now)
    ap_rej_user_id = fields.Many2one('res.users', string="Approved By", readonly=True, 
                                     copy=False, ondelete='restrict')
    ap_rej_date = fields.Datetime(string="Approved Date", readonly=True, copy=False)
    inactive_user_id = fields.Many2one('res.users', string="Inactivated By", readonly=True,
                                 copy=False, ondelete='restrict')
    inactive_date = fields.Datetime(string='Inactivated Date', readonly=True, copy=False)
    update_user_id = fields.Many2one('res.users', string="Last Update By", readonly=True, copy=False,
                                    ondelete='restrict')
    update_date = fields.Datetime(string="Last Update Date", readonly=True, copy=False)

    ## Validation ##
    def validatoins(self, **kw):
        """ Validations """
        warning_msg = []

        if self.status in ('draft', 'editable'):
            res_config_rule = self.env['ir.config_parameter'].sudo().get_param('custom_properties.rule_checker_master')
            is_mgmt = self.env['res.users'].has_group('cm_user_mgmt.group_mgmt_admin')
            if res_config_rule and self.user_id == self.env.user and not(is_mgmt):
                warning_msg.append("Created user is not allow to approve the entry")
        
        if warning_msg:
            formatted_messages = "\n".join(warning_msg)
            raise UserError(formatted_messages)
        else:
            return True

    @api.constrains('name')
    def _check_name_constrains(self):

        def _special_char_check(value,label):
            if is_special_char(self.env,value):
                raise UserError(_('Special character is not allowed in %s field'%(label)))

        if self.name:
            _special_char_check(self.name,'mail name')
            
            name = self.name.upper().replace(" ", "")
            self.env.cr.execute(""" select upper(name)
            from cp_external_apis where upper(REPLACE(name, ' ', ''))  = '%s'
            and id != %s""" %(name, self.id))

            if self.env.cr.fetchone():
                raise UserError(_('External apis purpose must be unique'))

        return True

    def entry_approve(self):
        """ entry_approve """ 
        if self.status in ('draft', 'editable'):
            self.validatoins()
            self.write({
                    'status' : 'active',
                    'ap_rej_user_id': self.env.user.id,
                    'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S')
                })

        return True

    def entry_draft(self):
        """ entry_draft """
        if self.status == 'active':
            self.write({'status': 'editable'})

        return True

    def entry_inactive(self):
        """ entry_inactive """
        if self.status == 'active':
            if self.inactive_remark:
                if self.inactive_remark.strip():
                    if len(self.inactive_remark.strip())>= 10:
                        self.write({'status':'inactive',
                                    'inactive_user_id': self.env.user.id,
                                    'inactive_date': time.strftime('%Y-%m-%d %H:%M:%S')})
                    else:
                        raise UserError(
                            _('Minimum 10 characters are required for Inactive Remark'))
            else:
                raise UserError(
                    _('Inactive remark is must, Enter the remarks in Inactive Remark field'))
        else:
            raise UserError(
                    _('Unable to inactive other than active entry'))

        return True
    
    def unlink(self):
        """ Unlink """
        for rec in self:
            if rec.status not in ('draft'):
                raise UserError('You can not delete other than draft entries')
            if rec.status in ('draft'):
                models.Model.unlink(rec)
        return True

    def write(self, vals):
        """ write """
        vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                     'update_user_id': self.env.user.id})
        return super(CpExternalAPIs, self).write(vals)


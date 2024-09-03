
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

MAIL_TYPE =  [('transaction','Transaction Mail'),
              ('scheduler','Scheduler Mail')]

class CpMailConfiguration(models.Model):
    _name = 'cp.mail.configuration'
    _description = 'Custom Mail Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'avatar.mixin']
    #_order = 'id'

    mail_type = fields.Selection(selection=MAIL_TYPE, string='Mail Type',)
    model_name = fields.Many2one('ir.model','Model Name')
    name = fields.Char('Mail Name', index=True, copy=False)
    status = fields.Selection(selection=CUSTOM_STATUS, string="Status", readonly=True, store=True, copy=False, default='draft')
    subject = fields.Char('Subject')
    from_mail_id = fields.Char('From Email-ID')
    interval = fields.Char('Interval')
    inactive_remark = fields.Text(string="Inactive Remark", copy=False)
    note = fields.Html(string="Note", copy=False)

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
        
    # Child table declaration
    line_ids = fields.One2many('cp.mail.configuration.line', 'header_id', string='Mail Configuration Lines', copy=True)

    ## Validation ##
    def validatoins(self, **kw):
        """ Validations """
        warning_msg = []
        if not self.line_ids:
            warning_msg.append('System not allow to approve with empty line details')
        
        # ~ to_add = self.line_ids.filtered(lambda m: m.to_address is True).mapped('to_address')
        # ~ if not to_add:
            # ~ raise UserError('Minimum one to mail id is must')

        #self._user_email_validation()

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
    
    @api.constrains('line_ids')
    def _user_email_validation(self):

        to_addresses = []
        cc_addresses = []
        bcc_addresses = []
        for line in self.line_ids:
            if not (line.to_address or line.cc_address or line.bcc_address):
                raise UserError('Either you have to select To, Cc, or Bcc for: {}'.format(line.email))
            if line.email and is_valid_mail(line.email):
                raise UserError(_('Email is not valid, check the given email for: {}'.format(line.email)))
            if line.to_address:
                to_addresses.append(line.email)
            if line.cc_address:
                cc_addresses.append(line.email)
            if line.bcc_address:
                bcc_addresses.append(line.email)

        # Consolidate all email addresses
        all_addresses = to_addresses + cc_addresses + bcc_addresses

        # Check for duplicates
        duplicates = [email for email, count in Counter(all_addresses).items() if count > 1]

        if duplicates:
            raise UserError('Duplicate mail ids are not allowed. Remove duplicates: {}'.format(', '.join(duplicates)))

                
        if self.status == 'active':
            if not self.line_ids:
                raise UserError("You cannot delete all the entries; instead, you can inactivate the record")

        return True

    @api.constrains('name', 'mail_type')
    def _check_name_constrains(self):
        if self.name:
            self._special_char_check(self.name, 'mail name')
            
            name = self.name.upper().replace(" ", "")
            query = """ 
                SELECT UPPER(name),id
                FROM cp_mail_configuration 
                WHERE mail_type = %s
                AND UPPER(REPLACE(name, ' ', '')) = %s
                AND id != %s
            """

            params = [self.mail_type, name, self.id]

            if self.mail_type == 'transaction':
                query += "AND model_name = %s"
                params.append(self.model_name.id)

            self.env.cr.execute(query, params)
            if self.env.cr.fetchone():
                raise UserError(_('Mail config name must be unique'))
        return True

    @api.constrains('from_mail_id')
    def _check_email_constrains(self):
        if self.from_mail_id:
            self._special_char_check(self.from_mail_id, 'from email id')
            self._check_email(self.from_mail_id)
        return True

    @api.constrains('interval')
    def _check_interval_constrains(self):
        if self.interval:
            self._special_char_check(str(self.interval), 'interval')
        return True

    def _special_char_check(self, value, label):
        if is_special_char(self.env,value):
            raise UserError(_('Special character is not allowed in %s field' % (label)))
        return True

    def _check_email(self, value):
        if is_valid_mail(value):
            raise UserError(_('From email id is not valid, check the given email'))
        return True

    @api.onchange('mail_type')
    def mail_type_onchange(self):
        self.model_name = ''
        self.name = ''

    @api.onchange('model_name')
    def model_name_onchange(self):
        self.name = ''

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

    def mail_config_mailids_data(self, **kw):
        """Geting Mail Id's from mail configuration : mail_type,model_name,mail_name key value is must"""

        mail_type = kw.get('mail_type', '')
        model_name = kw.get('model_name', False)
        mail_name = kw.get('mail_name', '')

        email_from = []
        email_to = []
        email_cc = []
        email_bcc = []
        val = {'email_from': '', 'email_to': '', 'email_cc': '', 'email_bcc': ''}
        
        if mail_type: 
            if mail_type == 'transaction' and model_name and mail_name:
                mail_form_ids = self.env['cp.mail.configuration'].search(
                    [('active', '=', True),('status', '=', 'active'),('model_name','=',model_name),('name','=',mail_name)])
            elif mail_type == 'scheduler' and mail_name:
                mail_form_ids = self.env['cp.mail.configuration'].search(
                    [('active', '=', True),('status', '=', 'active'),('name','=',mail_name)])
            else:
                mail_form_ids = ''
        if mail_form_ids:
            for ids in mail_form_ids:
                email_from.append(ids.from_mail_id)
                for line in ids.line_ids:
                    if line.to_address:
                        email_to.append(line.email)
                    if line.cc_address:
                        email_cc.append(line.email)
                    if line.bcc_address:
                        email_bcc.append(line.email)

        val['email_from'] = email_from
        val['email_to'] = email_to
        val['email_cc'] = email_cc
        val['email_bcc'] = email_bcc

        return val

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
        return super(CpMailConfiguration, self).write(vals)

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the transaction views.
        """

        result = {
            'all_draft': 0,
            'all_active': 0,
            'all_inactive': 0,
            'all_editable': 0,
            'my_draft': 0,
            'my_active': 0,
            'my_inactive': 0,
            'my_editable': 0,
            'all_today_count': 0,
            'all_today_value': 0,
            'my_today_count': 0,
            'my_today_value': 0,
        }
        
        
        #counts
        cm_master = self.env['cp.mail.configuration']
        result['all_draft'] = cm_master.search_count([('status', '=', 'draft')])
        result['all_active'] = cm_master.search_count([('status', '=', 'active')])
        result['all_inactive'] = cm_master.search_count([('status', '=', 'inactive')])
        result['all_editable'] = cm_master.search_count([('status', '=', 'editable')])
        result['my_draft'] = cm_master.search_count([('status', '=', 'draft'), ('user_id', '=', self.env.uid)])
        result['my_active'] = cm_master.search_count([('status', '=', 'active'), ('user_id', '=', self.env.uid)])
        result['my_inactive'] = cm_master.search_count([('status', '=', 'inactive'), ('user_id', '=', self.env.uid)])
        result['my_editable'] = cm_master.search_count([('status', '=', 'editable'), ('user_id', '=', self.env.uid)])
              
        result['all_today_count'] = cm_master.search_count([('crt_date', '>=', fields.Date.today())])
        result['all_month_count'] = cm_master.search_count([('crt_date', '>=', datetime.today().replace(day=1))])
        result['my_today_count'] = cm_master.search_count([('user_id', '=', self.env.uid),('crt_date', '>=', fields.Date.today())])
        result['my_month_count'] = cm_master.search_count([('user_id', '=', self.env.uid), ('crt_date', '>=',datetime.today().replace(day=1))])

        return result

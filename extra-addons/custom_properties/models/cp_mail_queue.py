from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,date,timedelta
import time
from odoo.exceptions import UserError
import base64
import os
import smtplib
import logging
from odoo import tools

_logger = logging.getLogger(__name__)

CUSTOM_STATUS = [('pending', 'Pending'),
                 ('sent', 'Sent')]

ENTRY_MODE =  [('manual','Manual'),
               ('auto', 'Auto')]

class CpMailQueue(models.Model):
    _name = 'cp.mail.queue'
    _description = 'Mail Queue'
    _order = 'crt_date desc'

    name = fields.Char('Name', index=True, copy=False)
    mail_from = fields.Char('From')
    mail_to = fields.Char('To')
    mail_cc = fields.Char('Cc')
    mail_bcc = fields.Char('Bcc')
    subject = fields.Char('Subject')
    body = fields.Html('Body', sanitize=False)
    sent_time = fields.Datetime('Sent Time')
    status = fields.Selection(selection=CUSTOM_STATUS, string="Status", readonly=True, store=True, copy=False, default='pending')
    transaction_id = fields.Integer('Transaction ID')
    
    # Child table declaration
    line_ids = fields.One2many('cp.mail.queue.line', 'header_id', string='Mail Queue Lines', copy=True)

    ### Entry Info ###
    active = fields.Boolean(string="Visible", default=True)
    entry_mode = fields.Selection(selection=ENTRY_MODE, string="Entry Mode", readonly=True, copy=False,
                                  tracking=True, default='manual')
    company_id = fields.Many2one('res.company', required=True, copy=False,
                      readonly=True, default=lambda self: self.env.company, ondelete='restrict')
    user_id = fields.Many2one('res.users', string="Created By", readonly=True, copy=False,
                                    ondelete='restrict', default=lambda self: self.env.user.id)
    crt_date = fields.Datetime(string="Creation Date", readonly=True, copy=False, default=fields.Datetime.now)
    update_user_id = fields.Many2one('res.users', string="Last Update By", readonly=True, copy=False,
                                    ondelete='restrict')
    update_date = fields.Datetime(string="Last Update Date", readonly=True, copy=False)


    def batch_send_mail(self, **kw):
        """Batch send mail function"""

        if self.env.context.get('active_ids'):
            self.send_mail(queue_id=self.env.context.get('active_ids'))

        return True

    def send_mail(self, **kw):
        """send mail function"""
        today = date.today()
        if kw.get('queue_id'):
            queue_id = kw.get('queue_id')
        else:
            context = self._context.copy() or {}
            queue_id = [context.get("queue_id", False)]

        if queue_id and (queue_id[0] if type(queue_id) == list else True):
            que_search = self.search(
                [('id', 'in', queue_id if type(queue_id) == list else [queue_id]), ('status', '=', 'pending')])
        else:
            que_search = self.search(
                [('status', '=', 'pending'),('crt_date', '>=', today),
                ('crt_date', '<', today + timedelta(days=1))])

        if que_search:
            ir_mail_server = self.env['ir.mail_server']
            for que_rec in que_search:
                email_from = que_rec.mail_from
                email_to = que_rec.mail_to or ' '
                email_cc = que_rec.mail_cc or ' '
                email_bcc = que_rec.mail_bcc or ' '
                
                try:
                    if email_to != ' ' or email_cc != ' ':
                        if que_rec.body:
                            mimetype = None
                            attachment = []
                            for atch_line in que_rec.line_ids:
                                for ir_att in atch_line.attachment:
                                    if ir_att.store_fname:
                                        filestore_path = self.env['ir.attachment']._filestore()
                                        file_path = os.path.join(filestore_path, ir_att.store_fname)
                                        if file_path:
                                            with open(file_path, 'rb') as file:
                                                file_data = file.read()
                                                file_data = base64.b64encode(file_data).decode('utf-8')
                                                mimetype = ir_att.mimetype or mimetype
                                                attachment.append(
                                                    tuple([ir_att.name, base64.b64decode(file_data), mimetype]))

                            msg = ir_mail_server.build_email(
                                email_from=email_from,
                                email_to=[email_to],
                                subject=que_rec.subject,
                                attachments=attachment,
                                body=que_rec.body,
                                body_alternative=tools.html2plaintext(que_rec.body),
                                email_cc=[email_cc],
                                email_bcc=[email_bcc],
                                reply_to = email_cc,
                                object_id=que_rec.id and (
                                    '%s-%s' %
                                    (que_rec.id, 'cp.mail.queue')),
                                subtype='html',
                                subtype_alternative='plain')
      
                            res = ir_mail_server.send_email(msg, mail_server_id=1)

                            que_rec.write(
                                {'status': 'sent', 'sent_time': time.strftime('%Y-%m-%d %H:%M:%S')})
                except Exception as exception:
                    if exception:
                        additional_info = f"Ref: Mail Queue Id - {str(que_rec.id)} and Subject - {str(que_rec.subject)}"
                        error_message = f"{str(exception)}\n\n{additional_info}"
                        self.env['failure.history'].create({
                            'name': 'Send Mail',
                            'error': error_message,
                        })

        return True

    def create_mail_queue(self, **kw):
        """Mail Queue"""

        name = kw.get('name', '')
        trans_rec = kw.get('trans_rec', '')
        mail_from = kw.get('mail_from', 'erp-support@kggroup.in')
        email_to = kw.get('email_to', '')
        email_cc = kw.get('email_cc', '')
        email_bcc = kw.get('email_bcc', '')
        subject = kw.get('subject', '')
        body = kw.get('body', '')
        attachment = kw.get('attachment', False)
           
        if name and email_to and subject and body:

            queue_id = self.env['cp.mail.queue'].create(
                {
                    'name': name,
                    'crt_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'company_id': trans_rec.company_id.id if trans_rec and hasattr(trans_rec, 'company_id') else self.env.company.id,
                    'mail_from':mail_from,
                    'mail_to': email_to,
                    'mail_cc': email_cc,
                    'mail_bcc': email_bcc,
                    'transaction_id': trans_rec.id if trans_rec else False,
                    'subject': subject,
                    'body': body,
                    'entry_mode':'auto'})

            if queue_id and attachment and isinstance(attachment, models.BaseModel) and attachment._name == 'ir.attachment':
                for atch in attachment:
                    queue_line = self.env['cp.mail.queue.line'].create(
                                        {'header_id': queue_id.id, 'attachment': atch})
            return queue_id

        return True

    def write(self, vals):
        """ write """
        vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                     'update_user_id': self.env.user.id})
        return super(CpMailQueue, self).write(vals)


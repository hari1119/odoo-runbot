from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime,date,timedelta
import time
from odoo.exceptions import UserError
from collections import Counter

CUSTOM_STATUS = [('pending', 'Pending'),
                 ('sent', 'Sent')]

ENTRY_MODE =  [('manual','Manual'),
               ('auto', 'Auto')]

MESSAGE_TYPE =  [('sms', 'SMS'),
                 ('whatsapp', 'WhatsApp')]

class CpSmsQueue(models.Model):
    _name = 'cp.sms.queue'
    _description = 'SMS Queue'
    _order = 'crt_date desc'

    name = fields.Char('Name')
    mobile_no = fields.Char('Mobile No')
    content_text = fields.Text('Text')
    message_type = fields.Selection(selection=MESSAGE_TYPE, string='Type')
    sent_time = fields.Datetime('Sent Time')
    status = fields.Selection(selection=CUSTOM_STATUS, string="Status", readonly=True, store=True, copy=False, default='pending')
    transaction_id = fields.Integer('Transaction ID')

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


    def batch_send_sms(self, **kw):
        """Batch send sms function"""

        if self.env.context.get('active_ids'):
            self.send_sms(queue_id=self.env.context.get('active_ids'))

        return True

    def batch_send_whats_app(self, **kw):
        """Batch send whatsapp function"""

        if self.env.context.get('active_ids'):
            self.send_whatsapp(wp_queue_id=self.env.context.get('active_ids'))

        return True

    #This function facilitates sending messages via sms.
    def send_sms(self, **kw):
        """send SMS function"""
        today = date.today()
        if kw.get('queue_id'):
            queue_id = kw.get('queue_id')
        else:
            context = self._context.copy() or {}
            queue_id = [context.get("queue_id", False)]

        if queue_id:
            pending_search = self.search(
                [('id', 'in', queue_id if type(queue_id) == list else [queue_id]),
                 ('status', '=', 'pending'), ('message_type', '=', 'sms')])
        else:
            pending_search = self.search(
                [('crt_date', '>=', today),('crt_date', '<', today + timedelta(days=1)),
                 ('status', '=', 'pending'), ('message_type', '=', 'sms')])

        if pending_search:
            for pending_rec in pending_search:                                        
                try:
                    url = ''
                    response = requests.post(url)
        
                    if response.status_code == 200:
                        pending_rec.write(
                                {'status': 'sent', 'sent_time': time.strftime('%Y-%m-%d %H:%M:%S')})
                        return True
                    else:
                        return False
                except:
                    return False

        return False
    
    #This function facilitates sending messages via WhatsApp.
    def send_whatsapp(self, **kw):
        """send whatsapp function"""
        today = date.today()
        if kw.get('wp_queue_id'):
            wp_queue_id = kw.get('wp_queue_id')
        else:
            context = self._context.copy() or {}
            wp_queue_id = [context.get("wp_queue_id", False)]
        
        if wp_queue_id:
            pending_search = self.search(
                [('id', 'in', wp_queue_id if type(wp_queue_id) == list else [wp_queue_id]),
                 ('status', '=', 'pending'), ('message_type', '=', 'whatsapp')])
        else:
            pending_search = self.search(
                [('crt_date', '>=', today),('crt_date', '<', today + timedelta(days=1)),
                 ('status', '=', 'pending'), ('message_type', '=', 'whatsapp')])

        if pending_search:
            for pending_rec in pending_search:
                try:
                    url = ''
                    response = requests.post(url)
                    if response.status_code == 200:
                        pending_rec.write(
                                {'status': 'sent', 'sent_time': time.strftime('%Y-%m-%d %H:%M:%S')})
                        return True
                    else:
                        return False
                except:
                    return False
        return False

    def create_sms_queue(self, **kw):
        """SMS Queue"""
        message_type = kw.get('message_type', '')
        sms_name = kw.get('sms_name', '')
        mobile_no = kw.get('mobile_no', '')
        content_text = kw.get('content_text', '')
        trans_rec = kw.get('trans_rec', '')
        
        if trans_rec and message_type and sms_name and mobile_no and content_text:
            queue_id = self.env['cp.sms.queue'].create(
                {
                    'message_type': message_type,
                    'name': sms_name,
                    'crt_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'company_id': trans_rec.company_id.id if trans_rec.company_id else '',
                    'transaction_id': trans_rec.id,
                    'mobile_no': mobile_no,
                    'content_text':content_text,
                    'entry_mode':'auto',
                })
            return queue_id
            
        return True

    def write(self, vals):
        """ write """
        vals.update({'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                     'update_user_id': self.env.user.id})
        return super(CpSmsQueue, self).write(vals)


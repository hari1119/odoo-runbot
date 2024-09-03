#-*- coding: utf-8 -*-

from odoo import models, fields, api


class CpScheduler(models.Model):
    _name = 'cp.scheduler'
    _description = 'Custom Scheduler'

    name = fields.Char()
    company_id = fields.Many2one('res.company', required=True, copy=False,
                      readonly=True, default=lambda self: self.env.company, ondelete='restrict')

    def custom_transaction_mail_action(self):
        '''custom_transaction_mail_action'''
        self.env['ct.transaction.scheduler'].custom_scheduler_mail()


    def auto_logger_mail(self):
        """ auto_logger_mail """
        mail_name = "Auto Logger Mail"

        log_count = self.env['ir.logging'].search_count([('level', '=', 'ERROR'),('create_date', '>=', fields.Date.today())])
        print('ddd',self)
        if log_count > 0:
            self.env.cr.execute("""select auto_logger_mail()""")
            data = self.env.cr.fetchall()
            subject = '#Need action#'
            
            if data[0][0] and subject:
                ### Mail Configuration ###
                mail_type='scheduler'
                mail_config_name='Auto Logger Mail'
                vals = self.env['cp.mail.configuration'].mail_config_mailids_data(mail_type=mail_type,mail_name=mail_config_name)

                email_to = ", ".join(vals.get('email_to', [])) if vals.get('email_to') else ''
                email_cc = ", ".join(vals.get('email_cc', [])) if vals.get('email_cc') else ''
                email_bcc = ", ".join(vals.get('email_bcc', [])) if vals.get('email_bcc') else ''
                email_from = ", ".join(vals.get('email_from', [])) if vals.get('email_from') else ''
                self.env['cp.mail.queue'].create_mail_queue(
                    name = mail_name, trans_rec = self, mail_from = email_from,
                    email_to = email_to, email_cc = email_cc, email_bcc = email_bcc,
                    subject = subject, body = data[0][0])
        return True

import datetime
import logging
import odoo
import time
from odoo import api, models
from odoo.fields import Datetime, _logger


class IrCron(models.Model):
    """ Inherits ir cron for add a feature that sends mail to admin
     each day, if any cron failed """
    _name = 'ir.cron'
    _inherit = ['ir.cron', 'mail.thread']

    @api.model
    def _callback(self, cron_name, server_action_id, job_id):
        """ Run the method associated to a given job. It takes care of logging
        and exception handling. Note that the user running the server action
        is the user calling this method. """
        try:
            if self.pool != self.pool.check_signaling():
                # the registry has changed, reload self in the new registry
                self.env.reset()
            log_depth = (None if _logger.isEnabledFor(logging.DEBUG) else 1)
            odoo.netsvc.log(_logger, logging.DEBUG, 'cron.object.execute',
                            (self._cr.dbname, self._uid, '*', cron_name,
                             server_action_id), depth=log_depth)
            start_time = False
            _logger.info('Starting job `%s`.', cron_name)
            if _logger.isEnabledFor(logging.DEBUG):
                start_time = time.time()
            self.env['ir.actions.server'].browse(server_action_id).run()
            _logger.info('Job `%s` done.', cron_name)
            if start_time and _logger.isEnabledFor(logging.DEBUG):
                end_time = time.time()
                _logger.debug('%.3fs (cron %s, server action %d with uid %d)',
                              end_time - start_time, cron_name,
                              server_action_id, self.env.uid)
            self.pool.signal_changes()
        except Exception as exception:
            self.pool.reset_changes()
            _logger.exception(
                "Call from cron %s for server action #%s failed in Job #%s",
                cron_name, server_action_id, job_id)
            if exception:
                self.env['failure.history'].create({
                    'name': cron_name,
                    'error': str(exception),
                })

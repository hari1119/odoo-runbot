import hashlib
import logging
import os
from datetime import datetime, timedelta
import random
import base64
import pytz
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class APIAccessToken(models.Model):
    _name = "api.access_token"

    token = fields.Char("Access Token", required=True)
    user_id = fields.Many2one("res.users", string="User", required=True)
    expires = fields.Datetime("Expires", required=True)


    def find_one_or_create_token(self, user_id=None, create=False):
        if not user_id:
            user_id = self.env.user.id
        access_token = (
            self.env["api.access_token"].sudo().search([("user_id", "=", user_id)], order="id DESC", limit=1)
        )
        if access_token:
            access_token = access_token[0]
            if access_token.has_expired():
                access_token = None
        if not access_token:
            return None
        return access_token.token

    def has_expired(self):
        self.ensure_one()

        local_tz = pytz.timezone('Asia/Kolkata')
        local_time = datetime.now(pytz.utc).astimezone(local_tz)
        current_datetime = local_time.replace(tzinfo=None)

        return current_datetime > self.expires

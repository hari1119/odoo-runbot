import json
import logging
from urllib import response
import werkzeug.wrappers
import os
from base64 import b64encode
import pytz
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

import odoo.modules.registry
from odoo.modules import module

import secrets

_logger = logging.getLogger(__name__)

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


class AccessToken(http.Controller):
    """ Login API"""

    @http.route("/api/login", methods=["POST","OPTIONS"], type="json", auth="none", csrf=False, cors='*')
    def token(self, **kw):
        json_data = json.loads(request.httprequest.data)

        input_user_name = json_data.get("username")
        input_password = json_data.get("password")

        if input_user_name:

            res_users = request.env['res.users'].sudo().search([
                ('status','=','active'),('login','=',input_user_name)])
            if res_users:
                #Expire date add with timedelta and +05.30hrs
                local_tz = pytz.timezone('Asia/Kolkata')
                local_time = datetime.now(pytz.utc).astimezone(local_tz)
                current_datetime = local_time.replace(tzinfo=None)
                expire_datetime = current_datetime + timedelta(days=30)

                #random token generate
                new_token = secrets.token_urlsafe(32)

                token_values = request.env['api.access_token'].sudo().create({
                            'user_id': res_users.id,
                            'expires': expire_datetime,
                            'token': str(new_token)})
                token_key_visible = [{
                                    "user_id": res_users.id,    
                                    "username": input_user_name,
                                    "access_token": str(new_token),
                                }]

                return {'status':200,'message':'success', 'data':token_key_visible}

            else:
                return {'status':401,'message':'Wrong Username and Password', 'data':[{}]}
        else :
            return {'status':401,'message':'Username and Password is must', 'data':[{}]}

######################################################################################


    @http.route("/api/login", methods=["DELETE"], type="json", auth="none", csrf=False, cors='*')
    def delete(self, **post):
        """ Token delete function"""
        _token = request.env["api.access_token"]
        access_token = request.httprequest.headers.get("Authorization")
        access_token = _token.sudo().search([("token", "=", access_token)])
        if not access_token:
            return {'status':400,'message':'No access token was provided in request', 'data':[{}]}
        for token in access_token:
            token.unlink()
        # Successful response:
        return {'status':200,'message':'Token successfully deleted', 'data':[{}], "delete": True}

##########################################################################################

    # Below one for odoo session management

    # ~ @http.route('/bharath/session_auth', type='json', auth="none")
    # ~ def _authenticate(self, db, login, password, base_location=None):
        # ~ if not http.db_filter([db]):
            # ~ raise AccessError("Database not found.")
        # ~ pre_uid = request.session.authenticate(db, login, password)
        # ~ if pre_uid != request.session.uid:
            # ~ # Crapy workaround for unupdatable Odoo Mobile App iOS (Thanks Apple :@) and Android
            # ~ # Correct behavior should be to raise AccessError("Renewing an expired session for user that has multi-factor-authentication is not supported. Please use /web/login instead.")
            # ~ return {'uid': None}

        # ~ request.session.db = db
        # ~ registry = odoo.modules.registry.Registry(db)
        # ~ with registry.cursor() as cr:
            # ~ env = odoo.api.Environment(cr, request.session.uid, request.session.context)
            # ~ if not request.db and not request.session.is_explicit:
                # ~ # request._save_session would not update the session_token
                # ~ # as it lacks an environment, rotating the session myself
                # ~ http.root.session_store.rotate(request.session, env)
                # ~ request.future_response.set_cookie(
                    # ~ 'session_id', request.session.sid,
                    # ~ max_age=http.SESSION_LIFETIME, httponly=True
                # ~ )
            # ~ return True


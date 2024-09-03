#-*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

import logging
import random
import psycopg2
from ast import literal_eval
from datetime import datetime, date

logger = logging.getLogger(__name__)

class CustomProperties(http.Controller):
    @http.route('/custom_properties/custom_properties', auth='public')
    def index(self, **kw):
         return "Hello, world"


    @http.route('/custom_properties/img/<string:filename>', auth='public')
    def get_image(self, filename):
        image_path = '/Odoo17/V1/Odoo17-Base/cm_addons/custom_properties/static/src/img/' + filename
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        return request.make_response(image_data, [('Content-Type', 'image/png')])

    @http.route('/custom_properties/videos/<string:filename>', auth='public')
    def get_vidoes(self, filename):
        video_path = '/Odoo17/V1/Odoo17-Base/cm_addons/custom_properties/static/src/videos/' + filename
        with open(video_path, 'rb') as video_file:
            video_data = video_file.read()
        return request.make_response(video_data, [('Content-Type', 'video/mp4')])

    @http.route('/dashboard/statistics', type='json', auth='user')
    def get_statistics(self):

        return {
            'average_quantity': random.randint(4, 12),
            'average_time': random.randint(4, 123),
            'nb_cancelled_orders': random.randint(0, 50),
            'nb_new_orders': random.randint(10, 200),
            'orders_by_size': {
                'm': random.randint(0, 150),
                's': random.randint(0, 150),
                'xl': random.randint(0, 150),
            },
            'total_amount': random.randint(100, 1000)
        }

    @http.route("/master/search", methods=["POST"], type="json",
                auth="user")
    def master_search(self, search):
        """ Master Search """
        data = []
        # Check if the query is not empty
        if search['query'] != '':
            # Get all models in the system in the res.config.settings
            config_settings = request.env['ir.config_parameter'].sudo().get_param(
                'custom_properties.master_search_installed_ids')
            if search['options'] == "only-name" and config_settings:
                config_settings_str = literal_eval(config_settings)
                # Convert to list of integers
                config_settings_ids = [int(id_str) for id_str in config_settings_str]
                # Fetch ir.module.module records for the selected module IDs
                config_modules = request.env['ir.module.module'].sudo().search([
                    ('id', 'in', config_settings_ids)])
                for module in config_modules:
                    # Execute a raw SQL query to search records in the current model
                    request.env.cr.execute(
                                    "SELECT name,id FROM %s WHERE name ILIKE '%s'" % (
                                        module.name, '%' + search['query'] + '%'))
                    records = request.env.cr.dictfetchall()
                    # If there are matching records, process and append them to temp_data
                    if records:
                        for record in records:
                            data.append([{
                                        'title': request.env[module.name.replace('_', '.')]._description,
                                        'fieldname': "Name",
                                        'row_data': record['name'],
                                        'rec_id': request.env[module.name.replace('_', '.')].\
                                 search([('id', '=', record['id'])], limit=1).id,
                                        'model': request.env[module.name.replace('_', '.')]._name
                                    }])
                        request.env.cr.commit()
            elif search['options'] == "global":
                try:
                    # Execute a raw SQL query to search records in the current model
                    request.env.cr.execute("select * from global_search('%s')"%('%'+ search['query'] + '%'))
                    # Fetch the results as a list of dictionaries
                    records = request.env.cr.dictfetchall()
                    if records:
                       for rec in records:
                           rec['title'] = request.env[rec['tablename'].replace('_', '.')]._description
                           rec['fieldname'] = rec['columnname'] #request.env[rec['tablename']._fields[rec['columnname']].string
                           rec['model'] = request.env[rec['tablename'].replace('_', '.')]._name
                           rec['rec_id'] = request.env[rec['tablename'].replace('_', '.')].\
                                 search([(rec['columnname'], '=', rec['row_data'])], limit=1).id
                           data.append([rec])
                    request.env.cr.commit()
                except Exception as e:
                    request.env.cr.rollback()
            else:
                pass
        print(search['options'],"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", data) 
        return data
    
    
    @http.route('/custom/popup/disable', type='json', auth='user')
    def disable_popup_notification(self, **kw):
        # Fetch data from the model
        user_id = kw.get('user_id')
        notify_name = kw.get('notify_name')
        if user_id and notify_name:
            try:
                notify_rec = request.env['cp.popup.notification']
                today_date = date.today()

                existing_record = notify_rec.search([
                    ('name', '=', notify_name),
                    ('user_id', '=', user_id),
                    ('entry_date', '=', today_date)
                ], limit=1)

                if not existing_record:
                    notify_rec.create({
                        'name': notify_name,
                        'user_id': user_id,
                        'entry_date': today_date
                    })

            except Exception as e:
                _logger.error(f"An error occurred: {e}")

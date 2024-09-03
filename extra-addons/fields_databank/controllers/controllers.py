# -*- coding: utf-8 -*-
from odoo import http
from collections import defaultdict
import json

class FieldsDatabank(http.Controller):
     @http.route('/fields_databank/details', auth='public')
     def fields_tacker(self, **kw):
         ir_model_fields = http.request.env['ir.model.fields'].search([('model_id', 'in',
                 [int(ir_model.id) for ir_model in http.request.env['ir.model'].search([('transient', '=', False),('model', 'in',
                 [ir_module_module.name.replace("_", ".")
                         for ir_module_module in http.request.env['ir.module.module'].search([('category_id', 'in',
                 [ir_module_category.id for ir_module_category in http.request.env['ir.module.category'].search([('name', '=',
                  "custom_modules"),('parent_id', 'in',
                 [ir_module_category.id for ir_module_category in http.request.env['ir.module.category'].search([('name', '=',
                   "KGiSL")]) if not ir_module_category.create_uid])]) if not ir_module_category.create_uid])])
                 if ir_module_module.name not in ['cm_base_inherit', 'cm_login_page','cm_user_mgmt','fields_databank']])])])])
         field_databank = http.request.env['ir.model.fields'].search([('model', '=', 'fields.databank')])
         unknow_fields = defaultdict(list)
         for key, value in [(field.model_id.name, field.name) for field in ir_model_fields if field.name not in [fields_databank_field.name
                for fields_databank_field in field_databank]]:
                unknow_fields[key].append(value)
         attributes_mismatch = [(field.model_id.name, { field.name : {
                         "required": "added" if field.required == field_databank.search([('name', '=', field.name)], limit=1).required else "want to add",
                         "size": "added" if field.required == field_databank.search([('name', '=', field.name)], limit=1).size else "want to add" ,
                         #"help": "added" if field.required == field_databank.search([('name', '=', field.name)], limit=1).help else "want to add" ,
                         "copied": "added" if field.required == field_databank.search([('name', '=', field.name)], limit=1).copied else "want to add" ,
                         #"readonly": "added" if field.required == field_databank.search([('name', '=', field.name)], limit=1).readonly else "want to add" ,
                         "index": "added" if field.required == field_databank.search([('name', '=', field.name)], limit=1).index else "want to add" ,
                         "tracking": "added" if field.required == field_databank.search([('name', '=', field.name)], limit=1).tracking else "want to add"
                }}) for field in ir_model_fields if field.name in [fields_databank_field.name
                for fields_databank_field in field_databank]]
         unknow_attributes = defaultdict(list)
         for key, value in attributes_mismatch:
             unknow_attributes[key].append(value)
         mismatching_attributes = [{model : attributes_mismatch} for model in dict(unknow_attributes)
                for attributes_mismatch in unknow_attributes[model]
                for field in attributes_mismatch if field in [fields_databank_field.name
                for fields_databank_field in field_databank] for fields_name,atts in attributes_mismatch.items()
                        if atts.get("required") != "added" or atts.get("size") != "added"
                        or atts.get("copied") != "added" #or atts.get("help") != "added"        
                        #or atts.get("readonly") != "added" or atts.get("index") != "added"
                        or atts.get("tracking") != "added"]
         with open('/Odoo17/V3/Odoo17-Base/cm_addons/fields_databank/missing_fields.txt', 'w') as f:
               for atts in mismatching_attributes:
                     f.write(str(dict(atts)) + '\n')
         return json.dumps({"unknown_fields": unknow_fields,"missing_attributes": mismatching_attributes})


#     @http.route('/fields_databank/fields_databank/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fields_databank.listing', {
#             'root': '/fields_databank/fields_databank',
#             'objects': http.request.env['fields_databank.fields_databank'].search([]),
#         })

#     @http.route('/fields_databank/fields_databank/objects/<model("fields_databank.fields_databank"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fields_databank.object', {
#             'object': obj
#         })


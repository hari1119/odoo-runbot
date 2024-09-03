# -*- coding: utf-8 -*-
{
    'name': "Fields Databank",
    'version': '0.1',
    'category': 'Technical',
    'summary': "Fields collection for Development",
    'description': """
Collection of the fields with the business logic and validation.
    """,
    'author': "Hari",
    'category': "KGiSL/custom_modules",
    'application' : True,
    'depends': ['base','product','uom', 'account','cm_master', 'custom_properties'],
    'data': [
        'security/ir.model.access.csv',
        'data/audit_rule_data.xml',
        'views/cm_fields_view.xml',
	'views/ir_model_fields_view.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': {
		'/fields_databank/static/img/smily.gif',
        },
    },
    'installable': True,
     'license': 'LGPL-3',
}


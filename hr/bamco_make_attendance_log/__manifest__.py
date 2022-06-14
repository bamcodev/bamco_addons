# -*- coding: utf-8 -*-
{
    'name': "make_attendance_log",

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','bamco_zk_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_attendance_zk_temp_inherit.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
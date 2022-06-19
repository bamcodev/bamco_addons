# -*- coding: utf-8 -*-
{
    'name': "Bamco HR Payroll Base",

    'summary': """
        """,

    'description': """
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll', 'hr_work_entry'],

    # always loaded
    'data': [
        'data/hr_payroll_structure_type.xml',
        'data/hr_payroll_structure.xml',
    ],
}

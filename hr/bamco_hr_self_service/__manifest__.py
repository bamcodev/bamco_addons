# -*- coding: utf-8 -*-
{
    'name': "Bamco Hr self service",

    'summary': """
        """,

    'description': """
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_holidays', 'hr_payroll',
                # 'sure_hr_loan',
                'hr_work_entry_contract',
                'hr_recruitment'],

    # always loaded
    'data': [
        'views/resource_calendar_leaves_inherit.xml',
        'views/self_service.xml',
        'views/hr_hiring_request.xml',
        'views/hr_transport.xml',
        'views/hr_excuse.xml',
        'views/hr_mission.xml',
        'views/hr_employee.xml',
        'views/hr_transport_rate.xml',
        'security/ir.model.access.csv',
    ],
}
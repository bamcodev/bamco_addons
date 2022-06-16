# -*- coding: utf-8 -*-
{
    'name': "bamco Hr late, early, absence attendance",

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
    'depends': ['resource', 'hr_attendance', 'hr_holidays', 'bamco_hr_payroll_base','bamco_hr_public_holidays'],

    # always loaded
    'data': [
        'views/resource_calendar.xml',
        'views/hr_attendance.xml',
        'views/hr_absence.xml',
        'views/late_early_time_interval.xml',
        'data/salary_rule.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
    ],
}
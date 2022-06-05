# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HREmployeeInh(models.Model):
    _inherit = 'hr.employee'

    attendance_id_char = fields.Char('الرقم الوظيفي')
    arabic_name = fields.Char('')

    private_mobile_no = fields.Char('رقم الجوال الخاص')
    personal_email = fields.Char('الايميل الشخصي')
    constatnt_phone_no = fields.Char('هاتف ثابت')
    current_address = fields.Char('العنوان الحالي')
    state = fields.Selection(string="Employee State", selection=[
        ('فترة التجربة','فترة التجربة'),
        ('على راس العمل', 'على راس العمل'),
        ('مجاز', 'مجاز'),
        ('معلق', 'معلق'),
        ('منتهي  خدماته', 'منتهي  خدماته'),

    ],default='على راس العمل' )
    area = fields.Many2one('hr.area',string='القسم')
    branch = fields.Many2one('hr.branch',string='الفرع')
    hiring_date = fields.Date(string='تاريخ الالتحاق')


# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HREmployeeInh(models.Model):
    _inherit = 'hr.employee'

    attendance_id_char = fields.Char('Attendance ID')
    arabic_name = fields.Char('')
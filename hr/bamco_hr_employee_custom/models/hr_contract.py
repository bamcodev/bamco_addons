# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRContract(models.Model):
    _inherit = 'hr.contract'

    contract_type = fields.Selection(string="نوع العقد", selection=[
        ('محدد', 'محدد'),
        ('غير محدد', 'غير محدد'),
        ('أخري', 'أخري'),
    ], default='محدد')


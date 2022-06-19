from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    number_excuse_per_month = fields.Float()
    max_excuse_period = fields.Float()

from odoo import models, fields, api, _


class HrCategories(models.Model):
    _name = 'hr.categories'

    name = fields.Char('Name',required=True)
    amount = fields.Float()


from odoo import models, fields, api, _


class HrDocumentType(models.Model):
    _name = 'hr.document.type'

    name = fields.Char()
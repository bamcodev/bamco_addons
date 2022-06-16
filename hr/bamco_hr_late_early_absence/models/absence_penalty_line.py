from odoo import models, fields, api, _


class AbsencePenaltyLine(models.Model):
    _name = 'absence.penalty.line'
    _order = 'id asc, sequence asc'

    sequence = fields.Integer(required=True)
    penalty_rate = fields.Float()
    resource_calendar_id = fields.Many2one('resource.calendar')
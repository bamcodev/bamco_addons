from odoo import models, fields, api, _


class LateEarlyPenaltyLine(models.Model):
    _name = 'late.early.penalty.line'
    _order = 'id asc, sequence asc'

    late_early_time_interval_id = fields.Many2one('late.early.time.interval')
    sequence = fields.Integer()
    penalty_value = fields.Float()
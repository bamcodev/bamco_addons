from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LateEarlyTimeInterval(models.Model):
    _name = 'late.early.time.interval'
    _order = 'id asc'

    resource_calendar_id = fields.Many2one('resource.calendar')
    time_interval = fields.Char(compute='_compute_time_interval')
    first_operator = fields.Selection([('<', '<'), ('<=', '<=')])
    first_operand = fields.Float()
    second_operator = fields.Selection([('<', '<'), ('<=', '<=')])
    second_operand = fields.Float()
    late_early_penalty_line_ids = fields.One2many('late.early.penalty.line', 'late_early_time_interval_id')

    @api.depends('first_operator', 'first_operand', 'second_operator', 'second_operand')
    def _compute_time_interval(self):
        for rec in self:
            float_to_time = lambda x: '{0:02.0f}:{1:02.0f}'.format(*divmod(x * 60, 60))
            if rec.first_operator:
                rec.time_interval = "%s%st" % (str(float_to_time(rec.first_operand)), str(rec.first_operator))
            if rec.second_operator:
                rec.time_interval += "%s%s" % (str(rec.second_operator), str(float_to_time(rec.second_operand)))
            else:
                rec.time_interval=str(0)

    @api.constrains('first_operand', 'second_operand')
    def _check_first_second_operand(self):
        for rec in self:
            if not rec.first_operand and not rec.second_operand:
                raise ValidationError("First & Second operand can't both be zero")
            if rec.first_operand and rec.second_operator:
                if rec.second_operand <= rec.first_operand:
                    raise ValidationError("Second operand can't be smaller than first operand")
                elif rec.first_operand < 0 or rec.second_operand < 0:
                    raise ValidationError("Can't using negative numbers in time interval (There is no time in negative)")
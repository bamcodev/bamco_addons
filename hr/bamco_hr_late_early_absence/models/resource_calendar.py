from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    schedule_type = fields.Selection([('fixed', 'Fixed'), ('flexible', 'Flexible'), ('open', 'Open')],
                                     default='fixed')

    flexible_hours = fields.Float()
    attendance_flexible_ids = fields.One2many('resource.calendar.attendance', 'calendar_id')

    absence_penalty_type = fields.Selection([('fixed', 'Fixed'), ('cumulative', 'Cumulative')], default='fixed')
    absence_penalty_fixed_rate = fields.Float(default=1)
    absence_penalty_line_ids = fields.One2many('absence.penalty.line', 'resource_calendar_id')

    late_arrive_penalty_type = fields.Selection([('fixed', 'Fixed'),
                                                 ('cumulative', 'Cumulative')], default='fixed')
    late_arrive_penalty_fixed_rate = fields.Float(default=1)
    late_arrive_penalty_line_ids = fields.One2many('late.early.time.interval', 'resource_calendar_id')

    early_leave_penalty_type = fields.Selection([('fixed', 'Fixed'),
                                                 ('cumulative', 'Cumulative')], default='fixed')
    early_leave_penalty_fixed_rate = fields.Float(default=1)
    early_leave_penalty_line_ids = fields.One2many('late.early.time.interval', 'resource_calendar_id')

    @api.constrains('late_arrive_penalty_type')
    def _check_late_arrive_penalty_line_ids(self):
        if self.late_arrive_penalty_type == 'cumulative':
            if not self.late_arrive_penalty_line_ids:
                raise ValidationError("No time intervals & polices defined!!")

    @api.constrains('early_leave_penalty_type')
    def _check_early_leave_penalty_line_ids(self):
        if self.early_leave_penalty_type == 'cumulative':
            if not self.early_leave_penalty_line_ids:
                raise ValidationError("No time intervals & polices defined!!")

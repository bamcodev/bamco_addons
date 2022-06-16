from odoo import models, fields, api, _


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    hour_from_flexible = fields.Float(compute='_compute_hour_from_flexible')
    hour_to_flexible = fields.Float(compute='_compute_hour_to_flexible')
    schedule_type = fields.Selection(related='calendar_id.schedule_type')

    @api.depends('calendar_id.flexible_hours', 'hour_from')
    def _compute_hour_from_flexible(self):
        for rec in self:
            rec.hour_from_flexible = (rec.hour_from + rec.calendar_id.flexible_hours) % 24

    @api.depends('calendar_id.flexible_hours', 'hour_to')
    def _compute_hour_to_flexible(self):
        for rec in self:
            rec.hour_to_flexible = (rec.hour_to + rec.calendar_id.flexible_hours) % 24

from odoo import models, fields, api, _
import math


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'


    consume_hours = fields.Float()

    @api.model
    def create(self, vals):
        res = super(ResourceCalendarLeaves, self).create(vals)
        res.consume_hours = (res.date_to - res.date_from).total_seconds() / 3600.0
        return res

    def reset_consume_hours(self):
        consume_hours=(self.date_to - self.date_from).total_seconds() / 3600.0
        self.write({'consume_hours': consume_hours})
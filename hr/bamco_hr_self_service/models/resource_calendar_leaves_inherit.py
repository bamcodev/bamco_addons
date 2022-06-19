from odoo import models, fields, api, _


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    mission_id = fields.Many2one('hr.mission')
    excuse_id = fields.Many2one('hr.excuse')

    # it's found in another module but make it here
    # not to depend on the other addon
    consume_hours = fields.Float()


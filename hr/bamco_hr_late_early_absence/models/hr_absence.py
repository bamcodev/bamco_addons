from odoo import models, fields, api, _


class HrAbsence(models.Model):
    _name = 'hr.absence'

    name = fields.Char(compute='_compute_name')
    employee_id = fields.Many2one('hr.employee')
    date = fields.Date()

    _sql_constraints = [('unique_absence', 'unique(employee_id, date)',
                         'Duplicate Absence record for same employee in same date.')]

    @api.depends('employee_id', 'date')
    def _compute_name(self):
        self.name = "%s for %s" % (self.employee_id.name, str(self.date))

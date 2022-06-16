from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AbstractModel(models.AbstractModel):
    _name = 'hr.self.service'

    employee_id = fields.Many2one('hr.employee')
    start_date = fields.Date()
    end_date = fields.Date()
    comment = fields.Char()
    state = fields.Selection([('draft', 'Draft'), ('approve', 'approved'), ('validate', 'Validated'), ('refuse', 'Refused')],
                             default='draft')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise UserError(_('End date can not be before Start date.'))

    def approve(self):
        self.state = 'approve'

    def validate(self):
        self.state = 'validate'

    def refuse(self):
        self.state = 'refuse'

    def draft(self):
        self.state = 'draft'


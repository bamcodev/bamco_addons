from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrContract(models.Model):
    _inherit = 'hr.contract'

    num_working_days_month = fields.Integer(default=30,
                                            help="Used as standard rate for overtime calculations regardless "
                                                 "the true working days")
    num_working_hours_day = fields.Integer(default=8,
                                           help="Used as standard rate for overtime calculations regardless "
                                                "the true working hours")
    is_insured = fields.Boolean(string="Is Insured?", default=True, tracking=True)
    fixed_insurance = fields.Float(string="Fixed Insurance Amount", required=False, tracking=True)

    @api.constrains('state')
    def constrain_state(self):
        employee_contracts = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
        if len(employee_contracts) > 1:
            error_message = "Multiple running contracts for employee: " + str(self.employee_id.name)
            raise UserError(error_message)

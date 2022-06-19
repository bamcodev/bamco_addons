from odoo import models, fields, api, _


class HrVariableAllowanceDeduction(models.Model):
    _name = 'hr.variable.allowance.deduction'

    employee_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract', compute='_get_contract_id', store=True)
    date = fields.Date()
    amount = fields.Float(readonly=True)
    add_amount = fields.Float('Add Amount')
    type = fields.Many2one('hr.variable.allowance.deduction.type')
    payslip_id = fields.Many2one('hr.payslip')

    @api.depends('employee_id')
    def _get_contract_id(self):
        running_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                           ('state', '=', 'open')])
        if running_contracts:
            self.contract_id = running_contracts[0].id

    @api.onchange('type','add_amount')
    def _set_amount(self):
        if self.type and self.contract_id:
            if self.type.calculation_method == 'fixed':
                self.amount = self.type.fixed_amount
                self.amount = -1 * self.add_amount
            elif self.type.calculation_method == 'percentage':
                self.amount = self.contract_id.wage * self.type.percentage_amount * 0.01
            elif self.type.calculation_method == 'work_day':
                self.amount = (self.contract_id.wage / 30.0) * self.type.work_day_amount
                self.amount = (self.contract_id.wage / 30.0) *  - self.add_amount
            elif self.type.calculation_method == 'work_hour':
                self.amount = (self.contract_id.wage / (30.0 * 8)) * self.type.work_hour_amount
                self.amount = (self.contract_id.wage / (30.0 * 8)) * - self.add_amount
            if self.type.type == 'deduction':
                self.amount *= -1



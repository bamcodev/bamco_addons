from odoo import models, fields, api, _


class HrVariableAllowanceDeductionLines(models.Model):
    _name = 'hr.variable.allowance.deduction.lines'

    employee_id = fields.Many2one('hr.employee')
    variable_allowance_deduction = fields.Many2one('hr.variable.allowance.deduction')
    contract_id = fields.Many2one('hr.contract', compute='_get_contract_id', store=True)
    total = fields.Float(compute='compute_total')
    number_of_days = fields.Float()
    type = fields.Many2many('hr.variable.allowance.deduction.type','lines_types','line_id','type_id')

    # def _get_categories(self):
    #     ids = []
    #     for m in self.type:
    #         ids.extend(m.category_ids.ids)
    #     return [('id', 'in', ids)]

    category_ids = fields.Many2many('hr.categories')
    payslip_id = fields.Many2one('hr.payslip')

    def compute_total(self):
        for rec in self:
            amount = 0
            for categ in rec.category_ids:
                for c in rec.type:
                    if categ in c.category_ids:
                        if c.type == 'allowance':
                            amount += categ.amount*rec.number_of_days
                        else:
                            amount -= categ.amount*rec.number_of_days
            rec.total = amount

    def compute_total_per_type(self,type):
        for rec in self:
            amount = 0
            for categ in rec.category_ids:
                for c in type:
                    if categ in c.category_ids:
                        if c.type == 'allowance':
                            amount += categ.amount*rec.number_of_days
                        else:
                            amount -= categ.amount*rec.number_of_days
            return amount

    @api.depends('employee_id')
    def _get_contract_id(self):
        running_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'open')])
        if running_contracts:
            self.contract_id = running_contracts[0].id

    # @api.onchange('type')
    # def _set_amount(self):
    #     if self.type and self.contract_id:
    #         if self.type.calculation_method == 'fixed':
    #             self.amount = self.type.fixed_amount
    #         elif self.type.calculation_method == 'percentage':
    #             self.amount = self.contract_id.wage * self.type.percentage_amount * 0.01
    #         elif self.type.calculation_method == 'work_day':
    #             self.amount = (self.contract_id.wage / 30.0) * self.type.work_day_amount
    #         elif self.type.calculation_method == 'work_hour':
    #             self.amount = (self.contract_id.wage / (30.0 * 8)) * self.type.work_hour_amount
    #
    #         if self.type.type == 'deduction':
    #             self.amount *= -1

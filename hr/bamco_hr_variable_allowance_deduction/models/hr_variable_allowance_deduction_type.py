from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrVariableAllowanceDeductionType(models.Model):
    _name = 'hr.variable.allowance.deduction.type'

    name = fields.Char()
    type = fields.Selection([('allowance', 'Allowance'), ('deduction', 'Deduction')])
    code = fields.Char()

    calculation_method = fields.Selection([('fixed', 'Fixed'),
                                           ('percentage', 'Percentage'),
                                           ('work_day', 'Work day'),
                                           ('work_hour', 'Work hour')
                                           ])
    fixed_amount = fields.Float()
    percentage_amount = fields.Float()
    work_day_amount = fields.Float()
    work_hour_amount = fields.Float()

    salary_rule_id = fields.Many2one('hr.salary.rule')
    payslip_input_type_id = fields.Many2one('hr.payslip.input.type')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Code already exists!'),
        ('name_unique', 'unique(name)', 'Name already exists!')
    ]

    def create_salary_rule(self):
        if not self.salary_rule_id:
            data = {
                'name': "%s salary rule" % self.name,
                'code': self.code,
                'category_id': self.env.ref('hr_payroll.ALW').id if self.type == 'allowance' else self.env.ref('hr_payroll.DED').id,
                'sequence': 5,
                'amount_select': 'code',
                'amount_python_compute':  'result = inputs.%s.amount'  % self.code if self.type == 'allowance' else 'result = -1*inputs.%s.amount'  % self.code,
                'condition_select': 'python',
                'condition_python': 'result = inputs.%s' % self.code,
                'struct_id': self.env.ref('bamco_hr_payroll_base.custom_default_payroll_structure').id
            }

            self.salary_rule_id = self.env['hr.salary.rule'].create(data)
            self.payslip_input_type_id = self.env['hr.payslip.input.type'].create({'name': self.name, 'code': self.code})

        else:
            raise UserError(_('Salary rule is already created before ( %s )') % self.salary_rule_id.name)
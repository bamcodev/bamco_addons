from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        variable_allowance_deduction = self.env['hr.variable.allowance.deduction.lines'] \
            .search([('employee_id', '=', res.employee_id.id),
                     ('variable_allowance_deduction.date', '>=', res.date_from),
                     ('variable_allowance_deduction.date', '<=', res.date_to)])
        data = {}
        for it in variable_allowance_deduction:
            for type in it.type:
                if type.code not in data:
                    data.update(
                        {type.code: {'amount': it.compute_total_per_type(type), 'input_type_id': type.payslip_input_type_id.id}})
                else:
                    data[type.code]['amount'] += it.compute_total_per_type(type)

        for it in data:
            if data[it]['amount']:
                res.write({'input_line_ids': [(0, 0, {
                    'input_type_id': data[it]['input_type_id'],
                    'amount': data[it]['amount']
                })]})

        for it in variable_allowance_deduction:
            it.payslip_id = res.id

        return res

from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    def compute_sheet(self):
        for rec in self:
            leaves = self.env['resource.calendar.leaves'].search(['|','|',('holiday_id.employee_id.id', '=', rec.employee_id.id),
             ('excuse_id.employee_id.id', '=', rec.employee_id.id),#added for get excuses
             ('mission_id.employee_id.id', '=', rec.employee_id.id) #added for get missions
             ])
            for it in leaves:
                it.reset_consume_hours()
        res = super(HrPayslip, self).compute_sheet()
        ##todo if worked
        for rec in self:
            leaves = self.env['resource.calendar.leaves'].search(['|','|',('holiday_id.employee_id.id', '=', rec.employee_id.id),
             ('excuse_id.employee_id.id', '=', rec.employee_id.id),#added for get excuses
             ('mission_id.employee_id.id', '=', rec.employee_id.id) #added for get missions
             ])
            for it in leaves:
                it.reset_consume_hours()
        ##
        return res

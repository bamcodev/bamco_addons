from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_ids = fields.One2many('hr.document', 'employee_id')

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        documents_types = self.env['hr.document.type'].search([])
        for dt in documents_types:
            self.env['hr.document'].create({'type_id': dt.id, 'employee_id': res.id})
        return res
from odoo import models, fields, api, _


class HrDocument(models.Model):
    _name = 'hr.document'

    employee_id = fields.Many2one('hr.employee')
    type_id = fields.Many2one("hr.document.type")
    documents_ids = fields.One2many('hr.document.binary', 'document_id')
    done = fields.Boolean(compute='_compute_done')

    @api.depends('documents_ids')
    def _compute_done(self):
        self.done = True if len(self.documents_ids) else False

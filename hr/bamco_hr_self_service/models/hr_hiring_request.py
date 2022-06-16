from odoo import models, fields, api, _

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    hiring_request_id = fields.Many2one('hr.hiring.request')

class HrHiringRequest(models.Model):
    _name = 'hr.hiring.request'

    name = fields.Char(compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee')
    job_id = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department', related='job_id.department_id')
    date = fields.Date()
    number_of_vacancies = fields.Integer()
    educational_degree = fields.Char()
    years_of_experience = fields.Integer()
    salary = fields.Float()
    require_travel = fields.Boolean()
    job_requirements = fields.Text()
    state = fields.Selection(string="State",
                             selection=[('open', 'Open'), ('cancel', 'Canceled'), ('done', 'Done')],
                             default='open',
                             required=False)
    type = fields.Selection([('replace', 'Replace Employee'), ('addition', 'Addition to current staff')])
    application_ids = fields.One2many('hr.applicant', 'hiring_request_id')

    # @api.multi
    def open(self):
        for rec in self:
            rec.state = 'open'

    # @api.multi
    def done(self):
        for rec in self:
            rec.state = 'done'

    # @api.multi
    def cancel(self):
        for rec in self:
            rec.state = 'cancel'


    @api.model
    def create(self, vals):
        res = super(HrHiringRequest, self).create(vals)
        res.employee_id = self.env.user.employee_ids[0] if self.env.user.employee_ids else False
        return res

    # @api.one
    @api.depends('job_id')
    def _compute_name(self):
        self.name = self.job_id.name

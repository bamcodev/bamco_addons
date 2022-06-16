from odoo import models, fields, api, _


class HrTransport(models.Model):
    _name = 'hr.transport'
    _inherit = 'hr.self.service'

    number_km = fields.Float()
    amount = fields.Float(compute='_compute_amount', store=True)

    @api.depends('number_km')
    def _compute_amount(self):
        rate = float(self.env['ir.config_parameter'].get_param('transport_rate', default=0))
        self.amount = self.number_km * rate



from odoo import models, fields, api, _


class HrTransportConfiguration(models.TransientModel):
    _name = 'hr.transport.configuration'

    transport_rate = fields.Float(store=True)

    def act_execute(self):
        self.env['ir.config_parameter'].set_param('transport_rate', (self.transport_rate or 1), )

    @api.model
    def default_get(self, fields):
        res = super(HrTransportConfiguration, self).default_get(fields)
        transport_rate = float(self.env['ir.config_parameter'].get_param('transport_rate', default=1))
        res2 = dict(transport_rate=transport_rate)
        res.update(res2)
        return res

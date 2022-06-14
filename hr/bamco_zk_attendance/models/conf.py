from odoo import models, fields, api,exceptions
class HrOvertimeSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'zk.attendance.setting'


    no_checkout_mode = fields.Selection([('default','Defaut Date'),('shift','Work Schedule')],string="No check")

    deflt_time = fields.Float(string="Default Time",default_model='zk.attendance.setting')

    api_ip = fields.Char(string="API IP")
    api_port = fields.Char(string="API Port", help="If port is left empty the request will be sent without a port")



    def set_values(self):
        super(HrOvertimeSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('zk.attendance.setting', 'no_checkout_mode', self.no_checkout_mode)
        IrDefault.set('zk.attendance.setting', 'deflt_time', self.deflt_time)
        IrDefault.set('zk.attendance.setting', 'api_ip', self.api_ip)
        IrDefault.set('zk.attendance.setting', 'api_port', self.api_port)


    @api.model
    def get_values(self):
        res = super(HrOvertimeSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(no_checkout_mode=IrDefault.get('zk.attendance.setting', 'no_checkout_mode'),
                   deflt_time=IrDefault.get('zk.attendance.setting', 'deflt_time'),
                   api_ip=IrDefault.get('zk.attendance.setting', 'api_ip'),
                   api_port=IrDefault.get('zk.attendance.setting', 'api_port')
                   )
        return res


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import datetime as time
LOGGER = logging.getLogger(__name__)

class hrattendanceinherit(models.Model):
    _inherit = 'hr.attendance'


    # def set_checkin_out(self):
    #     for rec in self:
    #         if rec.check_in:
    #             rec.tmp_check_in=datetime.strptime(str(rec.check_in),"%Y-%m-%d %H:%M:%S") #+ time.timedelta(hours=2)
    #         if rec.check_out:
    #             rec.tmp_check_out = datetime.strptime(str(rec.check_out), "%Y-%m-%d %H:%M:%S") #+ time.timedelta(hours=2)

class hrattendancezkinherit(models.Model):
    _inherit = 'hr.attendance.zk.temp'


    def make_logged(self):
        for rec in self:
            rec.logged = True


    def make_logged_false(self):
        for rec in self:
            rec.logged = False
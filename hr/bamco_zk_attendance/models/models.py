# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import json
from datetime import datetime
import datetime as delta
import datetime as time
import pytz
import requests
import logging
import dateutil
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('attendance_id_char', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)


class zk_attendance_tmp(models.Model):
    _name = 'hr.attendance.zk.temp'

    machine_id = fields.Many2one(comodel_name="hr.attendance.zk.machine", string="Attendance Machine", required=True)
    user_number = fields.Char(string="Machine User Id", index=True)
    user = fields.Many2one(comodel_name="hr.employee", compute="_compute_user", store=True)
    date = fields.Datetime(string="Date", index=True)
    local_date = fields.Datetime(string='Date', compute="_compute_local_date", store=True,
                                 help='for display only as the datetime of the system is showing as 2 hours after')
    date_temp = fields.Date(string="Date Temp", index=True, compute="_compute_date", store=True)
    inoutmode = fields.Char(string="In/Out Mode")
    logged = fields.Boolean(string="Logged", default=False)
    reversed = fields.Boolean(string='Reversed', defult=True)

    @api.model
    def sudo_create_log(self, args):
        # create record if not found
        cr = self._cr
        cr.execute("""
                            select * from hr_attendance_zk_temp where date='{}' and inoutmode='{}'
                            and user_number='{}' and  machine_id='{}';
                            """.format(args['date'],
                                       args['inoutmode'], args['user_number'],
                                       args['machine_id']
                                       ))
        found = True if len(cr.dictfetchall()) > 0 else False

        if not found:
            self.env['hr.attendance.zk.temp'].sudo().create(args)
        return True

    @api.depends('user_number')
    def _compute_user(self):
        for rec in self:
            if rec.user_number:
                emps = self.env['hr.employee'].search([])
                for emp in emps:
                    if emp.attendance_id_char == rec.user_number:
                        rec.user = emp.id

    @api.depends('date')
    def _compute_date(self):
        for rec in self:
            if rec.date:
                egypt_timezone = datetime.strptime(str(rec.date), "%Y-%m-%d %H:%M:%S") + time.timedelta(hours=2)
                rec.date_temp = egypt_timezone.date()

    @api.depends('date')
    def _compute_local_date(self):
        for record in self:
            if record.date:
                record.local_date = datetime.strptime(str(record.date), "%Y-%m-%d %H:%M:%S") + time.timedelta(hours=2)

    def timezone_correction(self):
        for rec in self.search([]):
            date_Temp = datetime.strptime(rec.date, "%Y-%m-%d %H:%M:%S")
            print("First: ", date_Temp.strftime("%Y/%m/%d %H:%M:%S"))
            local = pytz.timezone("Africa/Cairo")
            local_dt = pytz.utc.localize(date_Temp, is_dst=None)
            date_Temp = local_dt.astimezone(local)
            print("Second: ", date_Temp.strftime("%Y/%m/%d %H:%M:%S"))
            # local_iraq = pytz.timezone("Asia/Baghdad")
            # local_dt = date_Temp.replace(tzinfo=local_iraq)
            # date_Temp = local_dt.astimezone(pytz.utc)
            print("Final: ", date_Temp.strftime("%Y/%m/%d %H:%M:%S"))
            rec.date = date_Temp

    @api.model
    def process_data(self):
        # Process_data
        # responsible for processing attendance data by
        # getting all the data for each employee for each day
        # checking the earliest check in and latest checkout
        # and producing an hr.attendance record with it if
        # the data is complete in case of a missing checkout
        # the record is handled based on the default time option
        # in config if set to default time we use the tie value set in config
        # or if the selected option is shift we use the checkout time set for the day in his shift
        # with open("/home/ali/ERP/cention11/sv/custom/zkLogs.txt", 'a') as out:
        # if there is ay machine not pulled today "process will run if all machines pulled" only
        today_date = str((datetime.today() + time.timedelta(hours=2)).date())
        not_pulled_today = self.env['hr.attendance.zk.machine'].search(
            [('last_download_log', '<', today_date + ' 00:00:00')])

        if not_pulled_today:
            raise ValidationError(_('Machines must be downloaded first!'))

        conf = self.env['zk.attendance.setting'].get_values()
        today_date_val = str(time.date.today())
        records = self.search([('logged', '=', False),
                               ('date_temp', '!=', today_date_val)])
        date_in = None
        date_out = None
        employees = list(set(self.search([('logged', '=', False), ('user', "!=", False),
                                          ('date_temp', '!=', today_date_val)]).mapped('user_number')))
        for emp in employees:
            emp_obj = self.env['hr.employee'].search([('attendance_id_char', '=', emp)])
            if not emp_obj:
                continue
            datetime_list = records.filtered(lambda x: x.user_number == emp).mapped('date')
            dates = [x.date().strftime("%Y-%m-%d") for x in datetime_list]
            dates_unique = list(set(dates))
            for date in dates_unique:
                attendance_per_emp = records.filtered(
                    lambda x: x.user_number == emp and str(x.date_temp) == date).sorted()

                date_ins = attendance_per_emp

                if len(attendance_per_emp) < 1:
                    pass
                # in case of one check in a day,
                # create atrendance record with check in=check out
                elif date_ins:
                    date_out = max(date_ins.mapped('date'))
                    date_in = min(date_ins.mapped('date'))
                    local_check_in = date_in + time.timedelta(hours=2)
                    local_check_out = date_out + time.timedelta(hours=2)

                    self.env['hr.attendance'].create(
                        {'employee_id': emp_obj.id, 'check_in': date_in,
                         'local_check_in': local_check_in,
                         'local_check_out': local_check_out,
                         'check_out': date_out,
                         'missing_check': True if (local_check_in == local_check_out) else False,
                         })
                    attendance_per_emp.write({'logged': True})


class zk_attendance_machine(models.Model):
    _name = "hr.attendance.zk.machine"

    machine_number = fields.Integer(string="Machine Number", default=0, readonly=True)
    name = fields.Char(string="Name")
    ip = fields.Char(string="IP", required=True)
    port = fields.Integer(string="port", default=4370)
    sync = fields.Boolean(string="Synced", default=False)
    model = fields.Char(string="Model")
    date_sync = fields.Datetime(string="Sync Date")
    date_sync_success = fields.Datetime(string="Successful Sync Date")
    manual_upload_sync_date = fields.Datetime(string="Last Manual Upload Date")
    sync_error = fields.Text(string="Sync Error")
    last_download_log = fields.Datetime('Last Download Log')

    ##
    @api.model
    def get_machine_last_download(self, args=None):
        self=self.sudo()
        if args['machine_id']:
            last_download_log= str(self.env['hr.attendance.zk.machine'].sudo().search(
                [('id', '=', int(args['machine_id']))]).last_download_log)

            #subtract 5 days from last download log, for any missing data for last 5 days
            #to be pulled in odoo again, and by itself reqpition in log is not permitted
            last_download_log=datetime.strptime(last_download_log, "%Y-%m-%d %H:%M:%S")- delta.timedelta(5)
            return str(last_download_log)

    @api.model
    def update_machine_last_download(self, args=None):  # machine_id, last_download
        # return self.sudo().do_update_machine_last_download(machine_id, last_download)
        if args is None:
            args = {}
        return self.sudo().do_update_machine_last_download(args['machine_id'], args['last_datetime'])

    @api.model
    def do_update_machine_last_download(self, machine_id, last_download):
        # _logger.critical('Machine Id: ', str(machine_id))
        # _logger.critical('Last download', str(last_download))
        # found = self.env['hr.attendance.zk.machine'].search([('id', '=', int(machine_id))])
        # if found:
        #as sure save all data for all machines once,update last donwload for all machines
        found = self.env['hr.attendance.zk.machine'].search([])
        if found:
            for rec in found:
                rec.write({
                    'last_download_log': last_download
                })
        return True

    ##
    @api.model
    def create(self, values):
        res = super(zk_attendance_machine, self).create(values)
        res['machine_number'] = res.id
        return res

    @api.model
    def pull_machines(self):
        machines = self.search([])
        for machine in machines:
            machine.pull_attendance()

    def pull_attendance(self):
        # Pull attendance
        # function sends a request to the attendance api according to the ip and port set in the config
        # receives the data from the api and sets them in the attendance temp model with duplicate detection
        # with open("/home/mohamed/Desktop/zkAttendanceIntegration/AttendanceLogs.json", encoding="utf-8-sig") as f:
        #     # raise Warning(f)
        #     file = f.read()
        #     data = json.loads(file)
        #     raise Warning(data)

        ############################################
        conf = self.env['zk.attendance.setting'].get_values()
        if conf['api_ip'] == None:
            raise exceptions.ValidationError("Please configure API IP and port before pulling from the machines")
        if conf['api_port'] == None or conf['api_port'] == False:
            url = "http://%s/api/AttendanceMachines/%s/%s" % (str(conf['api_ip']), str(self.ip), str(self.port))
        else:
            url = "http://%s:%s/api/AttendanceMachines/%s/%s" % (
                str(conf['api_ip']), str(conf['api_port']), str(self.ip), str(self.port))

        res = requests.get(url)
        res = res.json()

        if len(res) > 0:
            for record in res:
                date_Temp = datetime.strptime(record["DateTimeRecord"], "%Y/%m/%d %H:%M:%S")
                local = pytz.timezone("Africa/Cairo")
                local_dt = local.localize(date_Temp, is_dst=None)
                date_Temp = local_dt.astimezone(pytz.utc)
                vals = {"machine_id": self.machine_number, "user_number": record["IndRegID"], "date": date_Temp,
                        "inoutmode": record["InOutMode"]}
                duplicate = self.env['hr.attendance.zk.temp'].search(
                    [("machine_id", '=', self.machine_number), ("user_number", '=', record["IndRegID"]),
                     ("date", '=', date_Temp.strftime("%Y-%m-%d %H:%M:%S")),
                     ("inoutmode", '=', record["InOutMode"])]) or False
                if not duplicate:
                    new_vals, vals = self.check_overlapping_shift(vals)

                    if new_vals:
                        self.env['hr.attendance.zk.temp'].create(vals)
                        self.env['hr.attendance.zk.temp'].create(new_vals)
                    else:
                        self.env['hr.attendance.zk.temp'].create(vals)

            self.sync = True
            self.sync_error = ""
            self.date_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.date_sync_success = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def check_overlapping_shift(self, vals):
        employee = self.env['hr.employee'].search([('attendance_id_char', '=', vals['user_number'])])
        if employee:
            shift = employee.resource_calendar_id.attendance_rel_ids
            shift_from = sum(shift.mapped('hour_from'))
            shift_to = sum(shift.mapped('hour_to'))
            datetime_obj = vals['date']
            new_vals = vals.copy()

            # 2nd Shift
            if shift_to == 0.0:
                if datetime_obj.hour <= 2:
                    privious_date = datetime_obj - delta.timedelta(1)
                    new_date = privious_date.replace(hour=21, minute=59, second=59)
                    new_vals['date'] = new_date
                    vals['logged'] = True
            # 3rd Shift
            elif shift_from == 0.0:
                if datetime_obj.hour == 21:
                    new_date = datetime_obj.replace(hour=22, minute=1, second=59)
                    new_vals['date'] = new_date
                    vals['logged'] = True
            # 12 hours
            elif shift[0].hour_from == 20.0:
                if datetime_obj.hour in [5, 6]:
                    new_date = datetime_obj - delta.timedelta(1)
                    new_vals['date'] = new_date
                    vals['logged'] = True
                    # vals['reversed'] = True
                    # new_vals['reversed'] = True

            else:
                new_vals = False
        else:
            new_vals = False

        return new_vals, vals

    def process(self):
        # if there is ay machine not pulled today "process will run if all machines pulled" only
        today_date = str((datetime.today() + time.timedelta(hours=2)).date())
        not_pulled_today = self.env['hr.attendance.zk.machine'].search(
            [('last_download_log', '<', today_date + ' 00:00:00')])

        if not_pulled_today:
            raise ValidationError(_('Machines must be downloaded first!'))

        # responsile to call process_data function from schedualed action
        self.env['hr.attendance.zk.temp'].process_data()


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    no_checkout = fields.Boolean(string="Missing Check-out", default=False)
    missing_check = fields.Boolean(string="Missing Check", default=False)

    no_check_in = fields.Boolean(string="Missing Check-in", default=False)

    local_check_in = fields.Datetime(string="Local Check In")
    local_check_out = fields.Datetime(string="Local Check Out")
    # tmp_check_in = fields.Datetime(string="Check in",compute="_compute_tmp_check_in",store=True)
    # tmp_check_out = fields.Datetime(string="Check out",compute="_compute_tmp_check_out",store=True)

    # @api.depends('check_in')
    # def _compute_tmp_check_in(self):
    #     for rec in self:
    #         if rec.check_in:
    #             rec.tmp_check_in=datetime.strptime(str(rec.check_in),"%Y-%m-%d %H:%M:%S") - time.timedelta(hours=2)

    # @api.depends('check_out')
    # def _compute_tmp_check_out(self):
    #     for rec in self:
    #         if rec.check_out:
    #             rec.tmp_check_out=datetime.strptime(str(rec.check_out),"%Y-%m-%d %H:%M:%S") - time.timedelta(hours=2)

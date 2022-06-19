# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.resource.models.resource import float_to_time
import calendar
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime, time, timedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    zk_emp_id = fields.Char(string="Employee Attendance ID", required=True)


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    schedule_type = fields.Selection([('fixed', 'Fixed'), ('flexible', 'Flexible'), ('open', 'Open')],
                                     default='fixed')


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    local_check_in = fields.Datetime(string="Local Check In")


class ExcelReportWizard(models.TransientModel):
    # _name = 'stock.card.report.excel'
    _name = 'hr.attendance.report.excel'

    excel_file = fields.Binary('Download report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)


class StockCardWizard(models.TransientModel):
    _name = 'hr.attendance.wizard'

    excel_file = fields.Binary('Download report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)
    start_date = fields.Date(string="Date From", required=True)
    end_date = fields.Date(string="Date To", required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employees")

    def stock_card_search(self):

        act = self.generate_excel()

        return {

            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance.report.excel',
            'res_id': act.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',

        }

    def get_employees_with_applied_filter(self):
        if self.employee_ids:
            return self.employee_ids

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.start_date > self.end_date:
            raise ValidationError(_('Start Date Can\'t be Before End Date'))

    def get_mapped_int_for_day(self, day_name):
        switcher = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,

        }

        return switcher.get(day_name, None)

    def get_date_str_from_datetime(self, field_datetime):
        date_type = fields.Datetime.from_string(str(field_datetime))
        date_str = date_type.date().strftime("%Y-%m-%d")
        return date_str

    def get_range_of_dates(self, start_date, end_date):
        start = datetime.strptime(self.get_date_str_from_datetime(start_date), "%Y-%m-%d")
        end = datetime.strptime(self.get_date_str_from_datetime(end_date), "%Y-%m-%d")
        date_array = \
            (start + timedelta(days=x) for x in range(0, (end - start).days + 1))
        date_range = []
        for date_object in date_array:
            date_range.append(date_object.strftime("%Y-%m-%d"))
        return date_range

    def get_day_name_from_date_str(self, date_str):
        day = datetime.strptime(date_str, '%Y-%m-%d').weekday()
        return (calendar.day_name[day])

    def get_time_difference(self, big_float, small_float):
        dateTimeA = datetime.combine(datetime.today(), big_float)
        dateTimeB = datetime.combine(datetime.today(), small_float)
        dateTimeDifferenceInMInutes = (dateTimeA - dateTimeB).total_seconds() / 60

        return round((dateTimeDifferenceInMInutes / 60), 2)

    def get_all_working_days(self, emp):
        self_sudo = self.sudo()
        date_from = fields.Datetime.from_string(self.start_date)
        date_to = fields.Datetime.from_string(self.end_date)
        all_days = []
        all_hours = 0.0
        range_of_dates = self_sudo.get_range_of_dates(date_from, date_to)
        if emp.resource_calendar_id:
            for day in range_of_dates:
                # considering the ontract start date
                if str(emp.contract_id.date_start) > str(datetime.strptime(day, "%Y-%m-%d").date()):
                    continue
                if emp.resource_calendar_id.schedule_type == 'fixed':
                    for fixed in emp.resource_calendar_id.attendance_ids:
                        if int(fixed.dayofweek) == self_sudo.get_mapped_int_for_day(
                                self_sudo.get_day_name_from_date_str(day)):
                            # all_days.append(fixed.dayofweek)
                            all_hours += round(self_sudo.get_time_difference(float_to_time(fixed.hour_to),
                                                                             float_to_time(fixed.hour_from)), 2)
                            if fixed.day_period == 'morning':
                                all_days.append(fixed.dayofweek)
                elif emp.resource_calendar_id.schedule_type == 'flexible':
                    for fixed in emp.resource_calendar_id.attendance_flexible_ids:

                        if int(fixed.dayofweek) == self_sudo.get_mapped_int_for_day(
                                self_sudo.get_day_name_from_date_str(day)):
                            all_days.append(fixed.dayofweek)
                            all_hours += round(self_sudo.get_time_difference(float_to_time(fixed.hour_to),
                                                                             float_to_time(fixed.hour_from)), 2)

        return {'all_hours': all_hours, 'all_days': len(all_days)}

    def get_actual_work_hours(self, emp):
        attendance = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                       ('check_in', '>=', str(self.start_date)),
                                                       ('check_in', '<=', str(self.end_date))
                                                       ]).mapped('worked_hours')
        work_hours = 0.0
        all_work_days = []
        if attendance:
            for rec in attendance:
                work_hours += rec
                all_work_days.append(rec)

        return {'work_hors': work_hours, 'all_work_days': len(all_work_days)}

    def get_time_off(self, emp):
        leaves = self.env['hr.leave'].search([('employee_id', '=', emp.id),
                                              ('date_from', '>=', str(self.start_date)),
                                              ('date_to', '<=', str(self.end_date)),
                                              ('state', '=', 'validate'),
                                              ]).mapped('number_of_days')
        leave_days = 0.0
        if leaves:
            for rec in leaves:
                leave_days += rec
        return leave_days

    def get_excuse(self, emp, start_date, end_date):
        excuse = self.env['hr.excuse'].search([('employee_id', '=', emp.id),
                                               ('start_date', '>=', str(start_date)),
                                               ('end_date', '<=', str(end_date)),
                                               ('state', '=', 'validate'),
                                               ]).mapped('period')
        hours = 0.0
        if excuse:
            for rec in excuse:
                hours += rec
        return hours

    def get_mission(self, emp, start_date, end_date):
        mission = self.env['hr.mission'].search([('employee_id', '=', emp.id),
                                                 ('start_date', '>=', str(start_date)),
                                                 ('end_date', '<=', str(end_date)),
                                                 ('state', '=', 'validate'),
                                                 ]).mapped('period')
        hours = 0.0
        if mission:
            for rec in mission:
                hours += rec
        # get no of hours per working day from schedule,divide hours no on it
        # then return the no of days for missions
        if emp.resource_calendar_id.hours_per_day > 0:
            return hours
        elif emp.resource_calendar_id.schedule_type == 'open' and emp.resource_calendar_id.hours_per_day == 0:
            return 0

        elif emp.resource_calendar_id.schedule_type != 'open' and emp.resource_calendar_id.hours_per_day == 0:
            raise ValidationError(_('Average Hour per Day must be non zero for employee: ' + emp.name))

    def get_time_str_from_datetime(self, field_datetime):
        date_type = fields.Datetime.from_string(field_datetime)
        time_str = date_type.strftime("%H:%M")
        return time_str

    def float_h_m(self, h_m):
        # h_m is str in format h:m, split to make a float
        h_m_splitted = h_m.split(':')
        print(h_m_splitted)
        hour = h_m_splitted[0]
        minute = h_m_splitted[1]
        print(minute)
        str_float = hour + '.' + str((int(minute) / 60)).split('.')[1]


        return float(str_float)

    def float_to_hours_minutes(self,hour_minute):
        hour = int(hour_minute)
        minutes = abs(hour_minute - hour)
        minutes_format = int(minutes * 60)
        time_format = str(hour) +':'+ str(minutes_format)
        return time_format

    def get_work_from_to_from_calendar(self, calender_obj_periods, dayofweek_int):
        work_from = 1000
        work_to = 0
        for atten_day in calender_obj_periods:
            if int(atten_day.dayofweek) == dayofweek_int:
                if atten_day.calendar_id.schedule_type == 'fixed':
                    if atten_day.hour_from < work_from:
                        work_from = atten_day.hour_from

                    if atten_day.hour_to > work_to:
                        work_to = atten_day.hour_to
                elif atten_day.calendar_id.schedule_type == 'flexible':
                    if atten_day.hour_from_flexible < work_from:
                        work_from = atten_day.hour_from_flexible

                    if atten_day.hour_to_flexible > work_to:
                        work_to = atten_day.hour_to_flexible

        print("::>>>>>>>>>>>>>>>>>>>>>>>>", {'work_from': work_from, 'work_to': work_to})
        return {'work_from': work_from, 'work_to': work_to}

    def late_or_early_left_or_well(self, local_check_in, local_check_out, emp):
        # get h:m fromcheck in and check out,
        # check if one if them is not as in working from, to with 1 minutes difference
        # return false,elseif both are as working from , to return true
        late = 0.0
        early = 0.0

        # states = {'late': 0, 'early_leave': 0, 'well': 1}
        day_date = self.get_date_str_from_datetime(local_check_in)
        day_name = self.get_day_name_from_date_str(day_date)

        day_name_as_int = self.get_mapped_int_for_day(day_name)
        local_check_in_h_m = self.get_time_str_from_datetime(local_check_in)
        local_check_out_h_m = self.get_time_str_from_datetime(local_check_out)

        work_from = None
        work_to = None

        # get from, to from working hours that have this day name
        if emp.resource_calendar_id:
            for atten_day in emp.resource_calendar_id.attendance_ids:
                if int(atten_day.dayofweek) == day_name_as_int:
                    print('atten_dayatten_day', atten_day)
                    work_day = self.get_work_from_to_from_calendar(emp.resource_calendar_id.attendance_ids,
                                                                   int(atten_day.dayofweek))
                    work_from = work_day['work_from']
                    work_to = work_day['work_to']
                    break

        if work_from and work_to:
            if (self.float_h_m(local_check_in_h_m) > work_from) and (
                    self.get_time_difference(local_check_in.time(), float_to_time(work_from)) > 0):
                late = self.get_time_difference(local_check_in.time(), float_to_time(work_from))
            if (self.float_h_m(local_check_out_h_m) < work_to) and (
                    self.get_time_difference(float_to_time(work_to), local_check_out.time()) > 0):
                early = self.get_time_difference(float_to_time(work_to), local_check_out.time())

        return (late + early)

    def get_late_hours(self, emp, date_from, date_to):
        # date_from = fields.Datetime.from_string(self.start_date) + datetime.timedelta(hours=2)
        # date_to = fields.Datetime.from_string(self.end_date) + datetime.timedelta(hours=2)
        attendance_data = self.env['hr.attendance'].search([('employee_id', '=', emp.id),
                                                            ('check_in', '>=', str(date_from)),
                                                            # self_sudo.start_date.strftime("%Y-%m-%d %I:%M:%S")
                                                            ('check_out', '<=', str(
                                                                date_to))])
        hours = 0.0
        for rec in attendance_data:
            print("rec.check_in>>>>>>>>>>>", rec.local_check_in)
            hours += self.late_or_early_left_or_well(rec.check_in, rec.check_out, rec.employee_id)
            print("::::::::>>>>>>>>>>", hours)
        return hours

    def get_absence(self,emp):
        absence_data = self.env['hr.absence'].search([('employee_id', '=', emp.id),
                                                            ('date', '>=', self.start_date),
                                                            ('date', '<=', self.end_date)])
        if absence_data:
            return len(absence_data)
        else:
            return 0

    def generate_excel(self):
        filename = "Attendance"

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('data')
        sheet.right_to_left()
        header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'bg_color': '#AAB7B8',
            'font_size': '10',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        super_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'bg_color': '#AAB7B8',
            'font_size': '20',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })

        col, row = 0, 7
        sheet.merge_range('B2:D3', 'Bamco', super_format)
        sheet.merge_range('F3:H3', str(fields.Datetime.now()), cell_format)
        sheet.write(5, 0, ' من تاريخ ', header_format)
        sheet.write(5, 1, str(self.start_date or ''), header_format)
        sheet.merge_range('D6:E6', 'الى تاريخ ', header_format)
        sheet.merge_range('F6:G6', str(self.end_date or ''), header_format)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 6, 15)

        headers = [
            'الرقم الوظيفى',
            'الاسم',
            'الساعات المطلوبه',
            'الساعات الفعليه',
            'ايام العمل المطلوبه',
            'ايام العمل الفعليه',
            'فرق ساعات عمل بالنقص ',
            'فرق ساعات عمل بالزيادة',
            'الاجازات ',
            'مغادرة عمل ',
            'غياب',
            ' التاخير',
        ]
        for h in headers:
            sheet.write(row, col, h, header_format)
            col += 1
        row += 1
        # function
        employees = self.get_employees_with_applied_filter()

        if not employees:
            raise ValidationError(_('No employees, Select employees please'))

        for emp in employees:
            horurs = self.get_all_working_days(emp)
            attendance = self.get_actual_work_hours(emp)
            leaves = self.get_time_off(emp)
            absence = self.get_absence(emp)

            excuse = self.get_excuse(emp, self.start_date, self.end_date)
            mission = self.get_mission(emp, self.start_date, self.end_date)
            late_hours = self.get_late_hours(emp, self.start_date, self.end_date)
            late_hours_val = ((late_hours - (
                    excuse + mission)) / emp.resource_calendar_id.hours_per_day) if emp.resource_calendar_id.hours_per_day > 0 else 0
            float_late = self.float_to_hours_minutes(round(late_hours_val,3))
            float_diff_hours = attendance['work_hors'] - horurs['all_hours']
            float_diff = self.float_to_hours_minutes(round(float_diff_hours,3))
            print("late_hours", late_hours)
            print("mission:::>>>>>", mission)
            # late = emp.filter_uncovered_late_attendance_intervals(emp.resource_calendar_id,self.start_date,self.end_date)
            # print(":::>>>>>>>>>>",late)
            col = 0
            sheet.write(row, col, str(emp.zk_emp_id or ''), cell_format)
            col += 1
            sheet.write(row, col, str(emp.name or ''), cell_format)
            col += 1
            sheet.write(row, col, horurs['all_hours'] or 0, cell_format)
            col += 1
            sheet.write(row, col, round(attendance['work_hors'], 2) or 0, cell_format)
            col += 1
            sheet.write(row, col, horurs['all_days'] or 0, cell_format)
            col += 1
            sheet.write(row, col, attendance['all_work_days'] or 0, cell_format)
            col += 1
            sheet.write(row, col, (float_diff) if attendance['work_hors'] < horurs['all_hours'] else 0, cell_format)
            col += 1
            sheet.write(row, col, (float_diff) if attendance['work_hors'] > horurs[
                'all_hours'] else 0, cell_format)
            col += 1
            sheet.write(row, col, leaves or 0, cell_format)
            col += 1

            if emp.resource_calendar_id.hours_per_day > 0:
                mission = mission / emp.resource_calendar_id.hours_per_day
            sheet.write(row, col, mission or 0, cell_format)
            col += 1
            sheet.write(row, col, absence or 0, cell_format)
            col += 1
            sheet.write(row, col, float_late or 0, cell_format)
            row += 1

        workbook.close()
        output.seek(0)

        self.write({'file_name': filename + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'})
        self.excel_file = base64.b64encode(output.read())

        context = {
            'file_name': self.file_name,
            'excel_file': self.excel_file,
        }

        act_id = self.env['hr.attendance.report.excel'].create(context)
        return act_id

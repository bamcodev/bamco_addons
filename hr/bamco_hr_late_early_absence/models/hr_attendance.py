from odoo import models, fields, api, _
from datetime import datetime, timedelta


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    late_attendance_hours = fields.Float()
    early_leave_hours = fields.Float()

    def time_to_float(self, time):
        return time.hour + time.minute / 60.0

    @api.constrains('check_in')
    def _compute_late_hours(self):
        if self.check_in:
            employee = self.employee_id

            #TODO: fix hard coded Timezone +2 "timedelta(hours=2)"
            check_in_datetime = datetime.strptime(str(self.check_in), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)

            check_in_date = check_in_datetime.date()
            check_in_day = str((int(datetime.strftime(check_in_date, '%w')) - 1) % 7)
            schedule_days = [it for it in employee.resource_calendar_id.attendance_ids]
            resource_calendar = employee.resource_calendar_id

            for it in schedule_days:
                if it.dayofweek == check_in_day:
                    if resource_calendar.schedule_type == 'fixed':
                        diff = self.time_to_float(check_in_datetime.time()) - it.hour_from
                        self.late_attendance_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'flexible':
                        diff = self.time_to_float(check_in_datetime.time()) - it.hour_from_flexible
                        self.late_attendance_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'open':
                        pass

                    break

    @api.constrains('check_in', 'check_out')
    def _compute_early_hours(self):
        if self.check_in and self.check_out:
            employee = self.employee_id

            # TODO: fix hard coded Timezone +2 "timedelta(hours=2)"
            check_in_datetime = datetime.strptime(str(self.check_in), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)
            check_out_datetime = datetime.strptime(str(self.check_out), '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)

            check_in_date = check_in_datetime.date()
            check_in_day = str((int(datetime.strftime(check_in_date, '%w')) - 1) % 7)
            schedule_days = [it for it in employee.resource_calendar_id.attendance_ids]
            resource_calendar = employee.resource_calendar_id

            for it in schedule_days:
                if it.dayofweek == check_in_day:
                    if resource_calendar.schedule_type == 'fixed':
                        diff = it.hour_to - self.time_to_float(check_out_datetime.time())
                        self.early_leave_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'flexible':
                        working_hours = it.hour_to - it.hour_from
                        hour_to_flexible = it.hour_to_flexible if it.hour_to_flexible >= it.hour_to else it.hour_to_flexible + 24.0
                        check_in_float = self.time_to_float(check_in_datetime.time())
                        check_out_float = self.time_to_float(check_out_datetime.time())
                        check_out_reference = min(hour_to_flexible, check_in_float + working_hours)

                        if check_out_float < check_in_float:
                            check_out_float += 24

                        diff = check_out_reference - check_out_float
                        self.early_leave_hours = diff if diff > 0 else 0
                    elif resource_calendar.schedule_type == 'open':
                        pass

                    break
        else:
            self.early_leave_hours = 0

    def day_is_a_public_holiday(self,day_date):
        found_public_holiday = self.env['hr.holidays.public.line'].sudo().search([(
            'date', '=', day_date
        )])
        if found_public_holiday:
            return True
        else:
            return False

    def is_absent(self, employee, date):
        date_dayofweek = str((int(datetime.strftime(date, '%w')) - 1) % 7)
        resource_calendar = employee.resource_calendar_id
        schedule_days = [it.dayofweek for it in resource_calendar.attendance_ids] if resource_calendar else []
        if date_dayofweek not in schedule_days:
            return False

        attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id)])
        for att in attendance:
            if datetime.strptime(str(att.check_in), '%Y-%m-%d %H:%M:%S').date() == date:
                return False

        leaves = self.env['resource.calendar.leaves'].search([('holiday_id.employee_id.id', '=', employee.id)])
        for leave in leaves:
            if leave.date_from.date() <= date <= leave.date_to.date():
                # if (leave.date_to - leave.date_from).total_seconds() / 3600.0 >= 24:
                    return False
        if self.day_is_a_public_holiday(date):
            return False

        return True

    @api.model
    def _update_absence(self, date=datetime.now().date()):
        previous_date = date - timedelta(days=1)
        employees = self.env['hr.employee'].search([])
        for emp in employees:
            if self.is_absent(emp, previous_date):
                self.env['hr.absence'].create({'employee_id': emp.id, 'date': previous_date})

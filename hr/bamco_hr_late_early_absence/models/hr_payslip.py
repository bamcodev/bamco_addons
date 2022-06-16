from odoo import models, fields, api, _, exceptions
from datetime import timedelta
from datetime import datetime, time
import calendar

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        for rec in self:
            leaves = self.env['resource.calendar.leaves'].search([('holiday_id.employee_id.id', '=', rec.employee_id.id)])
            for it in leaves:
                it.reset_consume_hours()
        res = super(HrPayslip, self).compute_sheet()
        #todo if worked
        for rec in self:
            leaves = self.env['resource.calendar.leaves'].search([('holiday_id.employee_id.id', '=', rec.employee_id.id)])
            for it in leaves:
                it.reset_consume_hours()
        #todo
        return res

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        absence_records = self.env['hr.absence'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', date_from),
            ('date', '<=', date_to)
        ])
        total_absence_days = len(absence_records)
        total_absence_hours = total_absence_days * self.employee_id.resource_calendar_id.hours_per_day if self.employee_id.resource_calendar_id else 0
        if total_absence_days and total_absence_hours:
            absence = {
                'name': 'Absence',
                'sequence': 3,
                'code': 'ABSENCE',
                'number_of_days': -1 * total_absence_days,
                'number_of_hours': -1 * total_absence_hours,
                'contract_id': self.contract_id.id,
            }
            res.append(absence)
        return res

    ##
    def get_date_str_from_datetime(self, field_datetime):
        date_type = fields.Datetime.from_string(str(field_datetime))
        date_str = date_type.date().strftime("%Y-%m-%d")
        return date_str
    ##
    def get_range_of_dates(self,start_date,end_date):
        start = datetime.strptime(self.get_date_str_from_datetime(start_date), "%Y-%m-%d")
        end = datetime.strptime(self.get_date_str_from_datetime(end_date), "%Y-%m-%d")
        date_array = \
            (start + timedelta(days=x) for x in range(0, (end - start).days+1))
        date_range=[]
        for date_object in date_array:
            date_range.append(date_object.strftime("%Y-%m-%d"))
        return date_range
    ##
    def get_day_name_from_date_str(self, date_str):
        day = datetime.strptime(date_str, '%Y-%m-%d').weekday()
        return (calendar.day_name[day])

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

    ##
    def day_name_not_working_day(self, date_str, emp):

        day_name = self.get_day_name_from_date_str(date_str)
        day_name = self.get_mapped_int_for_day(day_name)

        # search in working hours of that employee
        # if that day name availale and is holiday is false, return false , else return true

        if emp.resource_calendar_id:
            for atten_day in emp.resource_calendar_id.attendance_ids:
                if int(atten_day.dayofweek) == day_name :
                    return False

        not_working_day = True
        return not_working_day

    ##
    def is_public_holiday(self,atten_rec_date):
        for year_holidays in self.env['hr.holidays.public'].search([]):
            for holiday in year_holidays.line_ids:
                if atten_rec_date ==holiday.date:
                    return {'name':holiday.name}

        return {'name':None}
    ##
    def has_leave_request(self,atten_rec_date,emp):
        found_leave=self.env['hr.leave'].search([ ('employee_id','=',emp.id) , ('state','=','validate')
                                                     ,('request_date_to','>=', atten_rec_date) , ('request_date_from','<=', atten_rec_date)],limit=1)


        if found_leave:
            return {'type':found_leave.holiday_status_id.display_name}

        else:
            return {'type': None}

    ##
    def has_excuse_request(self,atten_rec_date,emp):

        found_excuse = self.env['hr.excuse'].search([('employee_id', '=', emp.id), ('state', '=', 'approved'),
                                                     ('date_to', '>=', atten_rec_date),
                                                     ('date_from', '<=', atten_rec_date)])



        if found_excuse:
            return {'reason': found_excuse.reason}

        else:
            return {'reason': None}

    ##get num of absence days from hr.absence model
    def get_custom_total_absence_days(self,payslip):


        return len(self.env['hr.absence'].search([('employee_id','=',payslip.employee_id.id),
                                                  ('date', '>=', payslip.date_from),
                                                  ('date', '<=', payslip.date_to)
                                                  ]))
    #search in system resources like leaves and public holidays to check if day is absent or not
    # def get_custom_total_absence_days(self,payslip):
    #     #check days in schlde and not found attendance for the employee for them
    #     attendance_recs=self.env['hr.attendance'].search([('employee_id', '=', payslip.employee_id.id),
    #                                                   ('check_in', '>=', payslip.date_from),
    #                                                   ('check_in', '<=', payslip.date_to)]).mapped('check_in')
    #     attendance_recs_dates=[]
    #     for rec in attendance_recs:
    #         attendance_recs_dates.append(str(rec.date()))
    #
    #     absence_days=0
    #     for rec in self.get_range_of_dates(payslip.date_from , payslip.date_to):
    #         if rec not in attendance_recs_dates:
    #             #make absence checks
    #             #if employee have not calendar_id, not set working time in employee profile
    #             #set attendance value for the day date as NA
    #             if  self.day_name_not_working_day(rec, payslip.employee_id):
    #                 continue
    #
    #             #if date is working day (checked in working days names found it)
    #             elif not self.day_name_not_working_day(rec, payslip.employee_id):
    #                 if(self.is_public_holiday(rec)['name']!=None):
    #                     continue
    #
    #                 elif  (self.has_leave_request(rec,payslip.employee_id)['type']!=None):
    #                     continue
    #
    #                 # elif (self.has_mission_request(rec,payslip.employee_id)['mission']!=None):
    #                 #     continue
    #                 # elif (self.has_excuse_request(rec,payslip.employee_id)['reason']!=None):
    #                 #     continue
    #                 else:
    #                     absence_days+=1
    #
    #     return absence_days
    #



    def compute_absence_penalty(self, payslip):
        payslip = payslip.dict
        resource_calendar = payslip.employee_id.resource_calendar_id
        wage = payslip.contract_id.wage
        wage_per_day = wage / 30.0
        total_absence_days = 0
        absence_penalty_rate = []
        for it in payslip.worked_days_line_ids:
            if it.code == 'ABSENCE':
                total_absence_days = abs(it.number_of_days)
                break
        #omara added 17 jan 2021
        total_absence_days=self.get_custom_total_absence_days(payslip)
        #omara
        if resource_calendar.absence_penalty_type == 'fixed':
            absence_penalty_rate = [resource_calendar.absence_penalty_fixed_rate]
        elif resource_calendar.absence_penalty_type == 'cumulative':
            absence_penalty_rate = [it.penalty_rate for it in resource_calendar.absence_penalty_line_ids]

        result = 0
        while total_absence_days > 0:
            if len(absence_penalty_rate) > 1:
                rate = absence_penalty_rate.pop(0)
                result += rate * wage_per_day
                total_absence_days -= 1
            elif len(absence_penalty_rate) == 1:
                result += absence_penalty_rate[0] * total_absence_days * wage_per_day
                total_absence_days = 0
            else:
                result += total_absence_days * wage_per_day
                total_absence_days = 0

        return -1 * result

    def _get_polices(self, raw_policy):
        res = []
        for it in raw_policy:
            res.append(
                ((it.first_operand, it.second_operand if it.second_operand else float('inf')),
                [x.penalty_value for x in it.late_early_penalty_line_ids]))
        return res

    def _get_policy_idx(self, time, policy):
        time=round(time,2)
        for idx, lp in enumerate(policy):
            if lp[0][0] <= time <= lp[0][1]:
                return idx
        return -1

    def compute_late_arrive_penalty(self, payslip):
        payslip = payslip.dict
        working_schedule = payslip.employee_id.resource_calendar_id
        wage = payslip.contract_id.wage
        wage_per_day = wage / 30.0
        if working_schedule.hours_per_day==0:
            raise exceptions.ValidationError(_("You must set Average Hours per day in work schudle of  "+payslip.employee_id.name))

            #
        wage_per_hour = wage_per_day / working_schedule.hours_per_day

        date_from = fields.Datetime.to_datetime(payslip.date_from)
        date_to = fields.Datetime.to_datetime(payslip.date_to) + timedelta(hours=23, minutes=59, seconds=59)
        late_days = self.env['hr.attendance'].search([('employee_id', '=', payslip.employee_id.id),
                                                      ('check_in', '>=', date_from),
                                                      ('check_in', '<=', date_to),
                                                      ('late_attendance_hours', '>', 0)])
        late_days = [DummyAttendance(it) for it in late_days]
        leaves = self.env['resource.calendar.leaves'].search([('holiday_id.employee_id.id', '=', payslip.employee_id.id)])
        for idx in range(0, len(late_days)):
            for leave in leaves:
                if late_days and leave.date_from.date() <= late_days[idx].check_in.date() <= leave.date_to.date():
                    if leave.consume_hours >= late_days[idx].late_attendance_hours:
                        leave.consume_hours -= late_days[idx].late_attendance_hours
                        late_days[idx].late_attendance_hours = 0
                    elif leave.consume_hours:
                        late_days[idx].late_attendance_hours -= leave.consume_hours
                        leave.consume_hours = 0

        late_days = list(filter(lambda a: a.late_attendance_hours != 0, late_days))
        total_late_hours = sum([it.late_attendance_hours for it in late_days])
        total_penalty = 0
        if working_schedule.late_arrive_penalty_type == 'fixed':
            total_penalty = total_late_hours * working_schedule.late_arrive_penalty_fixed_rate * wage_per_hour
        elif working_schedule.late_arrive_penalty_type == 'cumulative':
            late_policy = self._get_polices(working_schedule.late_arrive_penalty_line_ids)
            total_penalty_time = 0
            for it in late_days:
                idx = self._get_policy_idx(it.late_attendance_hours, late_policy)
                total_penalty_time += late_policy[idx][1][0] if late_policy and late_policy[idx][1] else it.late_attendance_hours
                if late_policy and len(late_policy[idx][1]) > 1:
                    late_policy[idx][1].pop(0)

            total_penalty = total_penalty_time * wage_per_hour

        return -1 * total_penalty

    def compute_early_leave_penalty(self, payslip):
        payslip = payslip.dict
        working_schedule = payslip.employee_id.resource_calendar_id
        wage = payslip.contract_id.wage
        wage_per_day = wage / 30.0
        wage_per_hour = wage_per_day / working_schedule.hours_per_day

        date_from = fields.Datetime.to_datetime(payslip.date_from)
        date_to = fields.Datetime.to_datetime(payslip.date_to) + timedelta(hours=23, minutes=59, seconds=59)
        early_days = self.env['hr.attendance'].search([('employee_id', '=', payslip.employee_id.id),
                                                      ('check_in', '>=', date_from),
                                                      ('check_in', '<=', date_to),
                                                      ('early_leave_hours', '>', 0)])
        early_days = [DummyAttendance(it) for it in early_days]
        leaves = self.env['resource.calendar.leaves'].search(
            [('holiday_id.employee_id.id', '=', payslip.employee_id.id)])
        for idx in range(0, len(early_days)):
            for leave in leaves:
                if early_days and leave.date_from.date() <= early_days[idx].check_in.date() <= leave.date_to.date():
                    if leave.consume_hours >= early_days[idx].early_leave_hours:
                        leave.consume_hours -= early_days[idx].early_leave_hours
                        early_days[idx].early_leave_hours = 0
                    elif leave.consume_hours:
                        early_days[idx].early_leave_hours -= leave.consume_hours
                        leave.consume_hours = 0

        early_days = list(filter(lambda a: a.early_leave_hours != 0, early_days))
        total_early_hours = sum([it.early_leave_hours for it in early_days])
        total_penalty = 0
        if working_schedule.early_leave_penalty_type == 'fixed':
            total_penalty = total_early_hours * working_schedule.early_leave_penalty_fixed_rate * wage_per_hour
        elif working_schedule.early_leave_penalty_type == 'cumulative':
            early_policy = self._get_polices(working_schedule.early_leave_penalty_line_ids)
            total_penalty_time = 0
            for it in early_days:
                idx = self._get_policy_idx(it.early_leave_hours, early_policy)
                total_penalty_time += early_policy[idx][1][0] if early_policy and early_policy[idx][1] else it.early_leave_hours
                if early_policy and len(early_policy[idx][1]) > 1:
                    early_policy[idx][1].pop(0)

            total_penalty = total_penalty_time * wage_per_hour

        return -1 * total_penalty


class DummyAttendance:
    def __init__(self, attendance):
        self.check_in = attendance.check_in
        self.check_out = attendance.check_out
        self.late_attendance_hours = attendance.late_attendance_hours
        self.early_leave_hours = attendance.early_leave_hours

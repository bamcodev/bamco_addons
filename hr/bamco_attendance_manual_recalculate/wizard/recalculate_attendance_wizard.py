# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
import datetime as delta
import datetime as time


class recalculate_attendance_wizard(models.TransientModel):
    _name = 'recalculate.attendance.wizard'

    start_date = fields.Date('Starting Date',required=True,
                            help='Will be recalcuted from this date,please note that this might depend on employees schedules')
    recalculate_attendance=fields.Boolean(string='Attendance')


    def delete_last_days_attendance(self,starting_date):
        #delete attendance
        starting_datetime = starting_date + ' 00:00:00'
        self.env['hr.attendance'].search([('local_check_in', '>=', starting_datetime)]).unlink()

        # delete overtime
        # for rec in self.env['over.time'].search([('date_from', '>=', starting_datetime),
        #                                          ('state','=','draft')
        #                                          ]):
        #     if rec.approbations:
        #         rec.approbations.unlink()
        #     rec.unlink()


        #make all logs logged=true
        # and make logs for them as false
        self.env['hr.attendance.zk.temp'].search([]).write({'logged': True})

        # to make attendance recalculated again from logs
        attendance_logs = self.env['hr.attendance.zk.temp'].search([
            ('date_temp', '>=', starting_date)])
        if attendance_logs:
            attendance_logs.write({'logged': False})


    def recalculate_data(self):
        if self.recalculate_attendance:
            #delete last attendance from starting date
            self.delete_last_days_attendance(str(self.start_date))
            #recalculate again
            self.env['hr.attendance.zk.temp'].process_data()

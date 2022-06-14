# -*- coding: utf-8 -*-
from odoo import http

# class MakeAttendanceLog(http.Controller):
#     @http.route('/make_attendance_log/make_attendance_log/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/make_attendance_log/make_attendance_log/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('make_attendance_log.listing', {
#             'root': '/make_attendance_log/make_attendance_log',
#             'objects': http.request.env['make_attendance_log.make_attendance_log'].search([]),
#         })

#     @http.route('/make_attendance_log/make_attendance_log/objects/<model("make_attendance_log.make_attendance_log"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('make_attendance_log.object', {
#             'object': obj
#         })
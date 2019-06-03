# -*- coding: utf-8 -*-
from odoo import http

# class NhExpiryReport(http.Controller):
#     @http.route('/nh_expiry_report/nh_expiry_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nh_expiry_report/nh_expiry_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nh_expiry_report.listing', {
#             'root': '/nh_expiry_report/nh_expiry_report',
#             'objects': http.request.env['nh_expiry_report.nh_expiry_report'].search([]),
#         })

#     @http.route('/nh_expiry_report/nh_expiry_report/objects/<model("nh_expiry_report.nh_expiry_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nh_expiry_report.object', {
#             'object': obj
#         })
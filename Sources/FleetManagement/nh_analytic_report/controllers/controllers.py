# -*- coding: utf-8 -*-
from odoo import http

# class NhAnalyticAccountsReport(http.Controller):
#     @http.route('/nh_analytic_accounts_report/nh_analytic_accounts_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nh_analytic_accounts_report/nh_analytic_accounts_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nh_analytic_accounts_report.listing', {
#             'root': '/nh_analytic_accounts_report/nh_analytic_accounts_report',
#             'objects': http.request.env['nh_analytic_accounts_report.nh_analytic_accounts_report'].search([]),
#         })

#     @http.route('/nh_analytic_accounts_report/nh_analytic_accounts_report/objects/<model("nh_analytic_accounts_report.nh_analytic_accounts_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nh_analytic_accounts_report.object', {
#             'object': obj
#         })
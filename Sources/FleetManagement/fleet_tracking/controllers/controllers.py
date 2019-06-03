# -*- coding: utf-8 -*-
from odoo import http

# class FleetTracking(http.Controller):
#     @http.route('/fleet_tracking/fleet_tracking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_tracking/fleet_tracking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_tracking.listing', {
#             'root': '/fleet_tracking/fleet_tracking',
#             'objects': http.request.env['fleet_tracking.fleet_tracking'].search([]),
#         })

#     @http.route('/fleet_tracking/fleet_tracking/objects/<model("fleet_tracking.fleet_tracking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_tracking.object', {
#             'object': obj
#         })
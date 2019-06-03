# -*- coding: utf-8 -*-
from odoo import http

# class ProductMoves3np(http.Controller):
#     @http.route('/product_moves_3np/product_moves_3np/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_moves_3np/product_moves_3np/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_moves_3np.listing', {
#             'root': '/product_moves_3np/product_moves_3np',
#             'objects': http.request.env['product_moves_3np.product_moves_3np'].search([]),
#         })

#     @http.route('/product_moves_3np/product_moves_3np/objects/<model("product_moves_3np.product_moves_3np"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_moves_3np.object', {
#             'object': obj
#         })
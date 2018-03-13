# -*- coding: utf-8 -*-
from openerp import http

# class SaleOrderOat(http.Controller):
#     @http.route('/sale_order_oat/sale_order_oat/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_oat/sale_order_oat/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_oat.listing', {
#             'root': '/sale_order_oat/sale_order_oat',
#             'objects': http.request.env['sale_order_oat.sale_order_oat'].search([]),
#         })

#     @http.route('/sale_order_oat/sale_order_oat/objects/<model("sale_order_oat.sale_order_oat"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_oat.object', {
#             'object': obj
#         })
# -*- coding: utf-8 -*-
# from odoo import http


# class Colegio(http.Controller):
#     @http.route('/colegio/colegio', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/colegio/colegio/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('colegio.listing', {
#             'root': '/colegio/colegio',
#             'objects': http.request.env['colegio.colegio'].search([]),
#         })

#     @http.route('/colegio/colegio/objects/<model("colegio.colegio"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('colegio.object', {
#             'object': obj
#         })


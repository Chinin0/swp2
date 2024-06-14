# -*- coding: utf-8 -*-
# from odoo import http


# class Estudiante(http.Controller):
#     @http.route('/estudiante/estudiante', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/estudiante/estudiante/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('estudiante.listing', {
#             'root': '/estudiante/estudiante',
#             'objects': http.request.env['estudiante.estudiante'].search([]),
#         })

#     @http.route('/estudiante/estudiante/objects/<model("estudiante.estudiante"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('estudiante.object', {
#             'object': obj
#         })


# -*- coding: utf-8 -*-

from odoo import models, fields, api


class colegio(models.Model):
    _name = 'colegio.colegio'
    _description = 'colegio.colegio'

    name = fields.Char()
    telefono = fields.Char()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

